from flask import Flask, request, jsonify, render_template_string, Response
import requests
import urllib3
import os
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# טוקן מהגדרות ורסל
YM_TOKEN = os.environ.get('YM_TOKEN')

@app.route('/api/get_config', methods=['GET'])
def get_config():
    return jsonify({"token": YM_TOKEN})

@app.route('/api/stream_audio')
def stream_audio():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing URL", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.yiddish24.com/'
    }

    try:
        # הורדה מלאה לזיכרון השרת כדי שנטפרי לא יחסום הזרמה (Streaming)
        print(f"DEBUG: Downloading {target_url}", file=sys.stderr)
        res = requests.get(target_url, headers=headers, timeout=120)
        
        if res.status_code != 200:
            return f"Error from source: {res.status_code}", res.status_code

        # החזרת הקובץ כקובץ אודיו רגיל
        return Response(
            res.content,
            content_type='audio/mpeg',
            headers={'Content-Disposition': 'attachment; filename=audio.mp3'}
        )
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}", file=sys.stderr)
        return str(e), 500

@app.route('/', methods=['GET'])
def home():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        return render_template_string(f.read())
