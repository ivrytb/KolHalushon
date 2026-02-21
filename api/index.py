from flask import Flask, request, Response
import requests
import urllib3

# זה המקבילה ל- "curl -k" - ביטול אזהרות SSL בשרת
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/api/download')
def download():
    url = request.args.get('url')
    if not url:
        return "קישור חסר", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://www.yiddish24.com/'
    }

    try:
        # כאן אנחנו מבצעים את ההורדה מהאתר המקורי (בדיוק כמו ה-CURL שעבד לך)
        req = requests.get(url, headers=headers, stream=True, verify=False, timeout=30)
        
        def generate():
            for chunk in req.iter_content(chunk_size=1024 * 1024): # מנות של 1MB
                if chunk:
                    yield chunk

        # שליחת הקובץ אליך למחשב
        return Response(
            generate(),
            content_type='audio/mpeg',
            headers={
                "Content-Disposition": "attachment; filename=music_file.mp3",
                "Content-Transfer-Encoding": "binary" # עוזר לנטפרי להבין שזה קובץ להעברה
            }
        )
    except Exception as e:
        return f"Error: {str(e)}", 500
