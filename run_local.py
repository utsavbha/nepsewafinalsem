#!/usr/bin/env python3
"""Run NepSewa on your machine (same app as `python main.py`, host 0.0.0.0 for LAN testing)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, init_db

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8001))
    print("NepSewa local server")
    print(f"  http://127.0.0.1:{port}/")
    print(f"  http://127.0.0.1:{port}/health")
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
