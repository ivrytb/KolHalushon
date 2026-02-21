from flask import Flask, request, jsonify, render_template_string
import requests
import urllib3
import uuid
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
        return jsonify({"error": "YM_TOKEN missing"}), 500
    if not target_url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        unique_id = str(uuid.uuid4())
        
        # שם קובץ מספרי בלבד - מבוסס על זמן (למשל: 1740182400)
        # ימות המשיח דורשים סיומת .wav כדי שההמרה תעבוד נכון
        numeric_name = str(int(time.time()))
        filename = f"{numeric_name}.wav"
        
        # נתיב נקי: ivr2:KolMevaser/1740182400.wav
        dest_path = f"ivr2:KolMevaser/{filename}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.yiddish24.com/'
        }

        y24_res = requests.get(target_url, headers=headers, stream=True, timeout=60)
        if y24_res.status_code != 200:
            return jsonify({"error": f"Y24 blocked access: {y24_res.status_code}"}), 403

        total_size = int(y24_res.headers.get('content-length', 0))
        chunk_size = 5 * 1024 * 1024 
        part_index = 0
        byte_offset = 0

        for chunk in y24_res.iter_content(chunk_size=chunk_size):
            if not chunk: break
            
            upload_params = {
                'token': YM_TOKEN,
                'path': dest_path,
                'qquuid': unique_id,
                'qqpartindex': part_index,
                'qqpartbyteoffset': byte_offset,
                'qqchunksize': len(chunk),
                'qqtotalfilesize': total_size if total_size > 0 else byte_offset + len(chunk),
                'qqfilename': filename,
                'uploader': 'yemot-admin'
            }
            
            files = {'qqfile': (filename, chunk, 'audio/wav')}
            
            requests.post("https://www.call2all.co.il/ym/api/UploadFile", 
                          files=files, data=upload_params, timeout=60)
            
            byte_offset += len(chunk)
            part_index += 1

        # שלב הסיום - כאן אנחנו מוודאים שהקובץ הופך ל-wav טלפוני
        done_params = {
            'token': YM_TOKEN,
            'path': dest_path,
            'qquuid': unique_id,
            'qqfilename': filename,
            'qqtotalfilesize': byte_offset,
            'qqtotalparts': part_index,
            'convertAudio': 1 
        }
        
        done_res = requests.get("https://www.call2all.co.il/ym/api/UploadFile", params=done_params)
        done_data = done_res.json()

        if done_data.get('status') == 'success':
            # לינק הורדה סופי עם שם מספרי
            download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?token={YM_TOKEN}&path={dest_path}"
            return jsonify({"status": "success", "download_url": download_url})
        else:
            return jsonify({"error": done_data.get('message')}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
