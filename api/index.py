from flask import Flask, request, jsonify, render_template_string, Response
import requests
import urllib3
import time
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# שליפת הטוקן ממשתנה הסביבה בורסל
YM_TOKEN = os.environ.get('YM_TOKEN')

def get_index_html():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'index.html')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "<h1>Error: index.html not found</h1>"

@app.route('/', methods=['GET'])
def home():
    return render_template_string(get_index_html())

@app.route('/api/upload_to_ym', methods=['POST'])
def upload_to_ym():
    data = request.get_json()
    target_url = data.get('url')

    if not YM_TOKEN:
        return jsonify({"error": "YM_TOKEN missing in Vercel settings"}), 500
    if not target_url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        # 1. יצירת שם קובץ מספרי ונתיב לימות המשיח
        numeric_name = str(int(time.time()))
        filename = f"{numeric_name}.wav"
        dest_path = f"ivr2:KolMevaser/{filename}"

        # 2. הורדה מהמקור עם תחפושת דפדפן
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': 'https://www.yiddish24.com/',
            'Range': 'bytes=0-'
        }
        y24_res = requests.get(target_url, headers=headers, timeout=60)
        y24_res.raise_for_status()

        # 3. העלאה לימות המשיח
        payload = {
            'token': YM_TOKEN,
            'path': dest_path,
            'convertAudio': '1'
        }
        files = {'upload': (filename, y24_res.content, 'audio/wav')}
        
        ym_res = requests.post("https://www.call2all.co.il/ym/api/UploadFile", data=payload, files=files, timeout=120)

        # 4. בדיקת הצלחה
        try:
            res_json = ym_res.json()
            is_ok = res_json.get('success') is True or res_json.get('status') == 'success'
        except:
            is_ok = 'success":true' in ym_res.text.lower() or 'status":"success' in ym_res.text.lower()

        if is_ok:
            download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?token={YM_TOKEN}&path={dest_path}"
            return jsonify({"status": "success", "download_url": download_url})
        else:
            return jsonify({"error": f"Upload failed: {ym_res.text}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/proxy_download', methods=['GET'])
def proxy_download():
    """נתיב המתווך שמאפשר קביעת שם קובץ אישי בהורדה"""
    target_url = request.args.get('url')
    custom_name = request.args.get('name', 'lesson')
    
    if not target_url:
        return "Missing URL", 400

    try:
        res = requests.get(target_url, stream=True, timeout=60)
        res.raise_for_status()

        def generate():
            for chunk in res.iter_content(chunk_size=8192):
                yield chunk

        # יצירת כותרת שמכריחה שם קובץ ספציפי
        headers = {
            'Content-Disposition': f'attachment; filename="{custom_name}.wav"',
            'Content-Type': 'audio/wav'
        }
        return Response(generate(), headers=headers)

    except Exception as e:
        return str(e), 500
