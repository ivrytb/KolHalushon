from flask import Flask, request, jsonify, render_template_string
import requests
import urllib3
import uuid
import time
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

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
        qquuid = str(uuid.uuid4())
        numeric_name = str(int(time.time()))
        filename = f"{numeric_name}.wav"
        dest_path = f"ivr2:KolMevaser/{filename}"

        # תחפושת דפדפן מלאה כדי לעקוף את ה-403 של Cloudfront
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'audio/mpeg,audio/*;q=0.9,*/*;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.yiddish24.com/',
            'Origin': 'https://www.yiddish24.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'audio',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'Range': 'bytes=0-' # מבקש את כל הקובץ מההתחלה
        }

        # יצירת Session ושליחת בקשת GET ל-Y24
        session = requests.Session()
        y24_res = session.get(target_url, headers=headers, stream=True, timeout=30)
        
        # אם עדיין יש 403, ננסה להחזיר את השגיאה המפורשת
        y24_res.raise_for_status()
        
        total_size = int(y24_res.headers.get('content-length', 0))
        chunk_size = 5 * 1024 * 1024 
        part_index = 0
        byte_offset = 0

        for chunk in y24_res.iter_content(chunk_size=chunk_size):
            if not chunk: break
            
            payload = {
                'qquuid': qquuid,
                'qqpartindex': part_index,
                'qqpartbyteoffset': byte_offset,
                'qqchunksize': len(chunk),
                'qqtotalfilesize': total_size if total_size > 0 else (byte_offset + len(chunk) + 1),
                'qqfilename': filename,
                'uploader': 'yemot-admin'
            }
            
            files = {'qqfile': (filename, chunk, 'audio/wav')}
            
            requests.post("https://www.call2all.co.il/ym/api/UploadFile", 
                          data=payload, files=files, timeout=60)
            
            byte_offset += len(chunk)
            part_index += 1

        # שלב הסיום - Done
        done_url = "https://www.call2all.co.il/ym/api/UploadFile"
        done_params = {
            'done': '',
            'token': YM_TOKEN,
            'path': dest_path,
            'qquuid': qquuid,
            'qqfilename': filename,
            'qqtotalfilesize': byte_offset,
            'qqtotalparts': part_index,
            'convertAudio': 1
        }
        
        final_res = requests.get(done_url, params=done_params, timeout=60)
        final_data = final_res.json()

        if final_data.get('status') == 'success':
            download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?token={YM_TOKEN}&path={dest_path}"
            return jsonify({"status": "success", "download_url": download_url})
        else:
            return jsonify({"error": f"Yemot Error: {final_data.get('message')}"}), 500

    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Yiddish24 Access Denied (403). They are blocking the server. {str(e)}"}), 403
    except Exception as e:
        return jsonify({"error": f"General Error: {str(e)}"}), 500
