#!/usr/bin/env python3
"""
Minimal test to check Flask app
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "NepSewa Test Server is Working! ✅"

@app.route("/test")
def test():
    return jsonify({
        "status": "success",
        "message": "Flask is working correctly",
        "server": "NepSewa Test"
    })

if __name__ == "__main__":
    print("🚀 Starting minimal test server...")
    print("📍 Visit: http://127.0.0.1:5000")
    print("📍 Test API: http://127.0.0.1:5000/test")
    app.run(debug=True, host='127.0.0.1', port=5000)