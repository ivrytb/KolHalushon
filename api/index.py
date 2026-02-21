from flask import Flask, request, jsonify, render_template_string
import requests
import urllib3
import time
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

YM_TOKEN = os.environ.get('YM_TOKEN')

@app.route('/api/upload_to_ym', methods=['POST'])
def upload_to_ym():
    data = request.get_json()
    target_url = data.get('url')

    if not YM_TOKEN:
        return jsonify({"error": "YM_TOKEN missing"}), 500
    if not target_url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        # שם קובץ מספרי נקי
        numeric_name = str(int(time.time()))
        filename = f"{numeric_name}.wav"
        dest_path = f"ivr2:KolMevaser/{filename}"

        # 1. משיכת הקובץ מ-Y24 לזיכרון השרת (עם ה-Headers שעוקפים 403)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.yiddish24.com/',
            'Range': 'bytes=0-'
        }
        
        y24_res = requests.get(target_url, headers=headers, timeout=60)
        y24_res.raise_for_status()
        
        # 2. הכנת השליחה לימות המשיח בבקשה אחת (Single Post)
        # ככה זה נראה בדיוק כמו בטופס ה-HTML ששלחת
        payload = {
            'token': YM_TOKEN,
            'path': dest_path,
            'convertAudio': '1'
        }
        
        # הפרמטר 'upload' תואם ל-name="upload" מהטופס ששלחת
        files = {
            'upload': (filename, y24_res.content, 'audio/wav')
        }
        
        # שליחה לימות המשיח
        ym_res = requests.post(
            "https://www.call2all.co.il/ym/api/UploadFile",
            data=payload,
            files=files,
            timeout=120 # זמן המתנה ארוך יותר להעלאה מלאה
        )
        
        ym_data = ym_res.json()

        if ym_data.get('status') == 'success':
            download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?token={YM_TOKEN}&path={dest_path}"
            return jsonify({"status": "success", "download_url": download_url})
        else:
            return jsonify({"error": f"Yemot Error: {ym_data.get('message')}"}), 500

    except Exception as e:
        return jsonify({"error": f"Process Error: {str(e)}"}), 500
