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
        return jsonify({"error": "YM_TOKEN missing in Vercel"}), 500
    if not target_url:
        return jsonify({"error": "Missing target URL"}), 400

    try:
        # 1. הכנות ראשוניות
        qquuid = str(uuid.uuid4())
        numeric_name = str(int(time.time()))
        filename = f"{numeric_name}.wav" # סיומת wav חובה להמרה
        dest_path = f"ivr2:KolMevaser/{filename}"

        # 2. הורדת הקובץ מ-Y24 כ-Stream
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        y24_res = requests.get(target_url, headers=headers, stream=True, timeout=60)
        y24_res.raise_for_status()
        
        total_size = int(y24_res.headers.get('content-length', 0))
        
        # 3. פיצול והעלאה (Chunks)
        chunk_size = 5 * 1024 * 1024 # 5MB לכל חלק
        part_index = 0
        byte_offset = 0

        # יצירת רשימה לאיסוף כל החלקים כדי לוודא שכולם עלו
        chunks_generator = y24_res.iter_content(chunk_size=chunk_size)
        
        for chunk in chunks_generator:
            if not chunk:
                break
            
            current_chunk_size = len(chunk)
            
            # בניית ה-Form Data בדיוק לפי הפרוטוקול של ימות
            payload = {
                'qquuid': qquuid,
                'qqpartindex': part_index,
                'qqpartbyteoffset': byte_offset,
                'qqchunksize': current_chunk_size,
                'qqtotalfilesize': total_size if total_size > 0 else (byte_offset + current_chunk_size + 1),
                'qqfilename': filename,
                'uploader': 'yemot-admin'
            }
            
            # שליחת החלק ב-POST
            files = {'qqfile': (filename, chunk, 'audio/wav')}
            
            # העלאה לכתובת ה-API הבסיסית
            upload_res = requests.post(
                "https://www.call2all.co.il/ym/api/UploadFile",
                data=payload,
                files=files,
                timeout=60
            )
            
            if upload_res.status_code != 200:
                return jsonify({"error": f"Failed at chunk {part_index}: {upload_res.text}"}), 500
            
            byte_offset += current_chunk_size
            part_index += 1

        # 4. שלב ב' - פקודת DONE (חיבור הקבצים)
        # הפעם הפנייה היא ל-UploadFile?done
        done_url = "https://www.call2all.co.il/ym/api/UploadFile"
        done_params = {
            'done': '', # מוסיף את ה-?done ל-URL
            'token': YM_TOKEN,
            'path': dest_path,
            'qquuid': qquuid,
            'qqfilename': filename,
            'qqtotalfilesize': byte_offset,
            'qqtotalparts': part_index,
            'convertAudio': 1
        }
        
        # שלב הסיום מתבצע ב-GET או POST (נשתמש ב-GET כמקובל ב-done)
        final_res = requests.get(done_url, params=done_params, timeout=60)
        final_data = final_res.json()

        if final_data.get('status') == 'success':
            # לינק הורדה סופי שנטפרי מאשרת
            download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?token={YM_TOKEN}&path={dest_path}"
            return jsonify({
                "status": "success",
                "download_url": download_url
            })
        else:
            return jsonify({"error": f"Yemot Done Error: {final_data.get('message')}"}), 500

    except Exception as e:
        return jsonify({"error": f"General Error: {str(e)}"}), 500
