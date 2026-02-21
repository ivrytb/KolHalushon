from flask import Flask, request, Response, render_template_string
import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

def get_html():
    try:
        # איתור הקובץ בתיקיית public
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'index.html')
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "HTML file not found"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # קבלת ה-URL מתוך ה-JSON שנשלח מהדף
        data = request.get_json()
        target_url = data.get('url')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://www.yiddish24.com/'
        }
        
        try:
            req = requests.get(target_url, headers=headers, stream=True, verify=False)
            # אנחנו מחזירים את הקובץ כ-Stream ישיר לדפדפן
            return Response(req.iter_content(chunk_size=1024*256), content_type='audio/mpeg')
        except Exception as e:
            return str(e), 500

    # אם זה GET - נשארים בדף הבית
    return render_template_string(get_html())
