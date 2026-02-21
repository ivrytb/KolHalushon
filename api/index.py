from flask import Flask, request, Response
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

@app.route('/api/download', methods=['POST']) # שינוי ל-POST
def download():
    # שליפת ה-URL מגוף הבקשה (Form Data)
    url = request.form.get('url')
    if not url:
        return "קישור חסר", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://www.yiddish24.com/'
    }

    try:
        req = requests.get(url, headers=headers, stream=True, verify=False, timeout=30)
        
        def generate():
            for chunk in req.iter_content(chunk_size=256 * 1024):
                if chunk:
                    yield chunk

        return Response(
            generate(),
            content_type='audio/mpeg',
            headers={
                "Content-Disposition": "attachment; filename=y24_music.mp3"
            }
        )
    except Exception as e:
        return f"Error: {str(e)}", 500
