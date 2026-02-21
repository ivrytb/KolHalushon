from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/api/download')
def download():
    url = request.args.get('url')
    if not url:
        return "Missing URL", 400

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://www.yiddish24.com/'
    }

    # השרת של ורסל מוריד את הקובץ מ-Cloudfront (מהיר מאוד)
    req = requests.get(url, headers=headers, stream=True, verify=False)
    
    # השרת מעביר את הקובץ ישירות לדפדפן שלך
    def generate():
        for chunk in req.iter_content(chunk_size=4096):
            yield chunk

    return Response(generate(), content_type='audio/mpeg', 
                    headers={"Content-Disposition": "attachment; filename=y24_audio.mp3"})
