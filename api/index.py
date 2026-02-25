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
    print("LOG: Fetching configuration (YM_TOKEN check)", file=sys.stderr)
    return jsonify({"token": YM_TOKEN})

@app.route('/api/stream_audio')
def stream_audio():
    target_url = request.args.get('url')
    print(f"LOG: Starting stream for URL: {target_url}", file=sys.stderr)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.yiddish24.com/',
        'Range': 'bytes=0-'
    }

    try:
        req = requests.get(target_url, headers=headers, stream=True, timeout=30)
        print(f"LOG: Source status code: {req.status_code}", file=sys.stderr)
        
        def generate():
            for chunk in req.iter_content(chunk_size=128 * 1024):
                yield chunk
        
        return Response(generate(), content_type=req.headers.get('content-type'))
    except Exception as e:
        print(f"LOG: ERROR in stream: {str(e)}", file=sys.stderr)
        return str(e), 500

@app.route('/', methods=['GET'])
def home():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        return render_template_string(f.read())
