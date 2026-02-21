from flask import Flask, request, Response
import requests
import urllib3
import os

# ביטול אזהרות SSL לטובת עבודה חלקה בנטפרי
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

def get_html_content():
    # איתור נתיב הקובץ index.html בצורה אבסולוטית בשרת
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        path = os.path.join(root_dir, 'public', 'index.html')
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>שגיאה בטעינת הממשק</h1><p>{str(e)}</p>"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # טיפול בבקשת הורדה (POST)
    if request.method == 'POST':
        target_url = request.form.get('url')
        if not target_url:
            return "נא להזין קישור תקין", 400

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.yiddish24.com/'
        }

        try:
            # הורדה מהמקור (Y24) ושליחה חזרה למשתמש ב-Stream
            req = requests.get(target_url, headers=headers, stream=True, verify=False, timeout=60)
            
            def generate():
                for chunk in req.iter_content(chunk_size=256 * 1024):
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
            return f"שגיאה בתהליך ההורדה: {str(e)}", 500

    # טיפול בכניסה לאתר (GET)
    return get_html_content()

# ורסל זקוק לאובייקט app
