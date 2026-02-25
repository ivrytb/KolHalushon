from flask import Flask, request, jsonify, render_template_string, Response
import requests
import urllib3
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

@app.route('/api/get_config', methods=['GET'])
def get_config():
    # מחזיר את הטוקן לדפדפן לצורך ההעלאה הישירה
    return jsonify({"token": YM_TOKEN})

@app.route('/api/stream_audio')
def stream_audio():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing URL", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.yiddish24.com/',
        'Range': 'bytes=0-'
    }

    try:
        req = requests.get(target_url, headers=headers, stream=True, timeout=30)
        def generate():
            for chunk in req.iter_content(chunk_size=128 * 1024):
                yield chunk
        
        return Response(generate(), content_type=req.headers.get('content-type'))
    except Exception as e:
        return str(e), 500
