from flask import Flask, request, Response
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

@app.route('/api/download', methods=['POST'])
def download():
    # תמיכה גם ב-JSON וגם בטופס רגיל
    data = request.get_json() if request.is_json else request.form
    target_url = data.get('url')

    if not target_url:
        return "URL is missing", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://www.yiddish24.com/'
    }

    try:
        # בדיקה שהלינק בכלל עובד לפני שמתחילים
        resp = requests.get(target_url, headers=headers, stream=True, verify=False, timeout=15)
        
        def generate():
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                if chunk:
                    yield chunk

        return Response(generate(), content_type='audio/mpeg')
    except Exception as e:
        return str(e), 500
