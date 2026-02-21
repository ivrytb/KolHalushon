from flask import Flask, request, Response, render_template_string
import requests
import urllib3
import os

# ביטול אזהרות SSL לטובת עבודה חלקה בנטפרי
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# פונקציה לקריאת ה-HTML מתיקיית public (למקרה שה-rewrite לא תופס)
def get_html_content():
    try:
        path = os.path.join(os.getcwd(), 'public', 'index.html')
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "<h1>Error: index.html not found in public folder</h1>"

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    # אם המשתמש שלח טופס ב-POST (בקשת הורדה)
    if request.method == 'POST':
        target_url = request.form.get('url')
        if not target_url:
            return "נא להזין כתובת תקינה", 400

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.yiddish24.com/'
        }

        try:
            # הורדה מהמקור ב-Stream
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
            return f"שגיאה בהורדה: {str(e)}", 500

    # אם זו כניסה רגילה (GET), נציג את ממשק המשתמש
    return render_template_string(get_html_content())
