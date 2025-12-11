from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

CORS(app)
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "ok",
        "message": "InnSights API is running"
    })

@app.route('/health', methods=['GET'])
def health():
    """Alternative health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "innsights-api"
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )