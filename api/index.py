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
        return jsonify({"error": "YM_TOKEN missing in Vercel settings"}), 500
    
    if not target_url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        unique_id = str(uuid.uuid4())
        timestamp = int(time.time())
        filename = f"y24_{timestamp}.mp3"
        dest_path = f"ivr2:KolMevaser/{filename}"

        # תחפושת דפדפן משופרת למניעת שגיאת 403
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.yiddish24.com/',
            'Origin': 'https://www.yiddish24.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'audio',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }

        # התחלת הורדה מ-Y24
        session = requests.Session() # שימוש ב-Session שומר על עוגיות וחיבור יציב
        y24_res = session.get(target_url, headers=headers, stream=True, timeout=60)
        
        # אם עדיין יש שגיאה, נחזיר אותה בצורה ברורה
        if y24_res.status_code != 200:
            return jsonify({"error": f"Yiddish24 blocked access (Status {y24_res.status_code}). Check the URL."}), 403

        total_size = int(y24_res.headers.get('content-length', 0))
        
        chunk_size = 5 * 1024 * 1024 
        part_index = 0
        byte_offset = 0

        for chunk in y24_res.iter_content(chunk_size=chunk_size):
            if not chunk:
                break
            
            current_chunk_size = len(chunk)
            
            upload_params = {
                'token': YM_TOKEN,
                'path': dest_path,
                'qquuid': unique_id,
                'qqpartindex': part_index,
                'qqpartbyteoffset': byte_offset,
                'qqchunksize': current_chunk_size,
                'qqtotalfilesize': total_size if total_size > 0 else byte_offset + current_chunk_size,
                'qqfilename': filename,
                'uploader': 'yemot-admin'
            }
            
            files = {'qqfile': (filename, chunk)}
            
            ym_res = requests.post("https://www.call2all.co.il/ym/api/UploadFile", 
                                   files=files, data=upload_params, timeout=60)
            
            if ym_res.status_code != 200:
                return jsonify({"error": f"Failed to upload part {part_index} to Yemot"}), 500
            
            byte_offset += current_chunk_size
            part_index += 1

        # סיום העלאה
        done_params = {
            'token': YM_TOKEN,
            'path': dest_path,
            'qquuid': unique_id,
            'qqfilename': filename,
            'qqtotalfilesize': byte_offset,
            'qqtotalparts': part_index,
            'convertAudio': 0
        }
        
        done_res = requests.get("https://www.call2all.co.il/ym/api/UploadFile", params=done_params)
        done_data = done_res.json()

        if done_data.get('status') == 'success':
            download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?token={YM_TOKEN}&path={dest_path}"
            return jsonify({
                "status": "success",
                "download_url": download_url
            })
        else:
            return jsonify({"error": f"Yemot error: {done_data.get('message')}"}), 500

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500
