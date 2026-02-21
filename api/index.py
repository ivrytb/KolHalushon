from flask import Flask, request, Response
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# הגדרה מפורשת שהנתיב מקבל POST
@app.route('/download', methods=['POST'])
def download_logic():
    target_url = request.form.get('url')
    if not target_url:
        return "קישור חסר", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://www.yiddish24.com/'
    }

    try:
        req = requests.get(target_url, headers=headers, stream=True, verify=False, timeout=60)
        
        def generate():
            for chunk in req.iter_content(chunk_size=512 * 1024): # חתיכות של חצי מגה
                if chunk:
                    yield chunk

        return Response(
            generate(),
            content_type='audio/mpeg',
            headers={
                "Content-Disposition": "attachment; filename=y24_audio.mp3",
                "Content-Transfer-Encoding": "binary"
            }
        )
    except Exception as e:
        return f"שגיאה: {str(e)}", 500

# ורסל דורשת שהאובייקט app יהיה זמין
