from flask import Flask, request, jsonify
import requests
import urllib3
import uuid
import time
import os # ספרייה שמאפשרת גישה למשתני סביבה

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# שליפת הטוקן ממשתנה הסביבה שהגדרת בורסל
YM_TOKEN = os.environ.get('YM_TOKEN')

@app.route('/api/upload_to_ym', methods=['POST'])
def upload_to_ym():
    data = request.get_json()
    target_url = data.get('url')

    # בדיקה שהטוקן הוגדר בורסל
    if not YM_TOKEN:
        return jsonify({"error": "משתנה הסביבה YM_TOKEN לא מוגדר בורסל"}), 500
    
    if not target_url:
        return jsonify({"error": "נא להזין לינק מ-Y24"}), 400

    try:
        unique_id = str(uuid.uuid4())
        timestamp = int(time.time())
        filename = f"y24_{timestamp}.mp3"
        dest_path = f"ivr2:KolMevaser/{filename}"

        headers = {'User-Agent': 'Mozilla/5.0'}
        y24_res = requests.get(target_url, headers=headers, stream=True, timeout=60)
        y24_res.raise_for_status()
        
        total_size = int(y24_res.headers.get('content-length', 0))
        
        chunk_size = 5 * 1024 * 1024 
        part_index = 0
        byte_offset = 0

        for chunk in y24_res.iter_content(chunk_size=chunk_size):
            if not chunk:
                break
            
            current_chunk_size = len(chunk)
            
            upload_params = {
                'token': YM_TOKEN, # שימוש בטוקן המאובטח
                'path': dest_path,
                'qquuid': unique_id,
                'qqpartindex': part_index,
                'qqpartbyteoffset': byte_offset,
                'qqchunksize': current_chunk_size,
                'qqtotalfilesize': total_size if total_size > 0 else "",
                'qqfilename': filename,
                'uploader': 'yemot-admin'
            }
            
            files = {'qqfile': (filename, chunk)}
            
            ym_res = requests.post("https://www.call2all.co.il/ym/api/UploadFile", 
                                   files=files, data=upload_params, timeout=60)
            
            if ym_res.status_code != 200:
                return jsonify({"error": f"נכשל בהעלאת חלק {part_index}"}), 500
            
            byte_offset += current_chunk_size
            part_index += 1

        done_params = {
            'token': YM_TOKEN, # שימוש בטוקן המאובטח
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
            return jsonify({"error": f"שגיאה מימות המשיח: {done_data.get('message')}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
