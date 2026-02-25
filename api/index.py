from flask import Flask, request, Response, render_template_string, jsonify
import requests
import os

app = Flask(__name__)
YM_TOKEN = os.environ.get('YM_TOKEN')

@app.route('/api/proxy_audio')
def proxy_audio():
    target_url = request.args.get('url')
    # ה-Headers שקול מבשר דורשים
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://www.yiddish24.com/'
    }
    
    def generate():
        # אנחנו מושכים מקול מבשר ומזרימים לימות המשיח
        r = requests.get(target_url, headers=headers, stream=True)
        for chunk in r.iter_content(chunk_size=1024*1024):
            yield chunk

    return Response(generate(), content_type='audio/mpeg')

@app.route('/api/get_config')
def get_config():
    return jsonify({"token": YM_TOKEN, "host": request.host})

@app.route('/')
def home():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        return render_template_string(f.read())
