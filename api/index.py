from flask import Flask, request, Response
import requests
import urllib3

# ביטול אזהרות SSL בטרמינל של השרת
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/api/download')
def download():
    url = request.args.get('url')
    if not url:
        return "קישור חסר", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.yiddish24.com/'
    }

    try:
        # השרת מוריד ללא בדיקת תעודה כדי למנוע תקלות מקומיות
        req = requests.get(url, headers=headers, stream=True, verify=False, timeout=15)
        
        def generate():
            # שליחת חתיכות קטנות של 128KB - אידיאלי למעבר חלק בנטפרי
            for chunk in req.iter_content(chunk_size=128 * 1024):
                if chunk:
                    yield chunk

        return Response(
        generate(),
        content_type='application/octet-stream',
        headers={
            "Content-Disposition": "attachment; filename=y24_file.pdf"
        }
    )
        
    except Exception as e:
        return f"שגיאה בשרת: {str(e)}", 500
