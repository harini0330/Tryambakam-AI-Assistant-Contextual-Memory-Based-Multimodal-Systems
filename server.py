from flask import Flask, send_from_directory
from backend.api import app

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

@app.route('/', endpoint='serve_index')
def serve_index():
    return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000) 