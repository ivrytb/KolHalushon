from flask import Flask, request, Response
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# הגדרנו שהשרת יגיב גם לכתובת ה-API וגם לכתובת הראשית
@app.route('/', methods=['GET', 'POST'])
@app.route('/api/download', methods=['POST'])
def handle_all():
    # אם זו בקשת POST, סימן ששלחנו לינק להורדה
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return "Missing URL", 400

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://www.yiddish24.com/'
        }

        try:
            req = requests.get(url, headers=headers, stream=True, verify=False, timeout=30)
            
            def generate():
                for chunk in req.iter_content(chunk_size=256 * 1024):
                    if chunk:
                        yield chunk

            return Response(
                generate(),
                content_type='audio/mpeg',
                headers={"Content-Disposition": "attachment; filename=audio_file.mp3"}
            )
        except Exception as e:
            return f"Error: {str(e)}", 500

    # אם זו בקשת GET רגילה (כשנכנסים לאתר), השרת פשוט יציג הודעה או כלום
    # כי ה-Vercel אמור להציג את ה-index.html מה-public
    return "Server is running", 200
