#!/usr/bin/env python3
"""
Minimal Flask app for Render deployment testing
"""

import os
from flask import Flask, jsonify

# Create Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NepSewa - Live!</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            a { color: #3498db; text-decoration: none; margin-right: 15px; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 NepSewa is Live on Render!</h1>
            <p>Your service marketplace platform has been successfully deployed!</p>
            <h3>Test Links:</h3>
            <p>
                <a href="/health">Health Check</a>
                <a href="/test">Test Route</a>
                <a href="/api/services">API Test</a>
            </p>
            <p><strong>Status:</strong> ✅ Deployment Successful</p>
        </div>
    </body>
    </html>
    """

@app.route("/test")
def test():
    return "<h1>✅ Test Route Works!</h1><p>Flask routing is working correctly on Render.</p>"

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "message": "NepSewa API is running on Render",
        "platform": "Render Cloud",
        "database": "not connected (minimal mode)"
    })

@app.route("/api/services")
def api_test():
    return jsonify({
        "success": True,
        "message": "API is working",
        "services": ["cleaning", "plumber", "electrician"]
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8001))
    print(f"🌐 Starting NepSewa test server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)