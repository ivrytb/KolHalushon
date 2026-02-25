from flask import Flask, request, jsonify, render_template_string, Response
import requests
import urllib3
import os
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

YM_TOKEN = os.environ.get('YM_TOKEN')

@app.route('/api/get_config', methods=['GET'])
def get_config():
    return jsonify({"token": YM_TOKEN})

@app.route('/api/stream_audio')
def stream_audio():
    target_url = request.args.get('url')
    if not target_url:
        return "URL missing", 400

    # כותרות (Headers) משופרות כדי להיראות כמו דפדפן אמיתי
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.yiddish24.com/',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
        'Connection': 'keep-alive'
    }

    try:
        print(f"DEBUG: Attempting to connect to: {target_url}", file=sys.stderr)
        
        # שימוש ב-Session לשיפור יציבות
        session = requests.Session()
        req = session.get(target_url, headers=headers, stream=True, timeout=15, verify=False)
        
        print(f"DEBUG: Source status: {req.status_code}", file=sys.stderr)
        
        if req.status_code != 200:
            return f"Source returned error {req.status_code}", req.status_code

        def generate():
            try:
                for chunk in req.iter_content(chunk_size=256 * 1024):
                    if chunk:
                        yield chunk
            except Exception as e:
                print(f"DEBUG ERROR during stream: {e}", file=sys.stderr)

        return Response(generate(), content_type=req.headers.get('content-type', 'audio/mpeg'))

    except Exception as e:
        print(f"DEBUG EXCEPTION: {str(e)}", file=sys.stderr)
        return str(e), 500

@app.route('/', methods=['GET'])
def home():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        return render_template_string(f.read())
