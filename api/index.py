from flask import Flask, request, Response, render_template_string
import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

def get_html():
    # ניסיון לאתר את הקובץ בנתיבים שונים שורסל משתמשת בהם
    paths = [
        os.path.join(os.getcwd(), 'public', 'index.html'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'index.html')
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    return "<h1>השרת פעיל</h1><p>אבל קובץ הממשק (index.html) לא נמצא בתיקיית public</p>"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # קבלת ה-URL בצורה הכי פשוטה שיש
        target_url = None
        if request.is_json:
            target_url = request.get_json().get('url')
        else:
            target_url = request.form.get('url')

        if not target_url:
            return "Missing URL", 400

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://www.yiddish24.com/'
        }
        
        try:
            # הורדה בשידור חי מהמקור
            req = requests.get(target_url, headers=headers, stream=True, verify=False, timeout=30)
            req.raise_for_status() # בודק אם הלינק של Y24 תקין
            
            return Response(
                req.iter_content(chunk_size=512 * 1024), 
                content_type='audio/mpeg',
                headers={"Content-Disposition": "attachment; filename=audio.mp3"}
            )
        except Exception as e:
            return str(e), 500

    return render_template_string(get_html())
