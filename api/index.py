from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)
YM_TOKEN = os.environ.get('YM_TOKEN')

@app.route('/api/get_config')
def get_config():
    return jsonify({"token": YM_TOKEN})

@app.route('/')
def home():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        return render_template_string(f.read())
