#!/usr/bin/env python3
"""
NepSewa Local Development Server
Run this for local development without PostgreSQL
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app from render_start.py
from render_start import initialize_app

if __name__ == "__main__":
    print("🚀 Starting NepSewa Local Development Server")
    print("📊 Using SQLite database for local development")
    
    # Initialize the app
    app = initialize_app()
    
    # Run the development server
    port = int(os.environ.get('PORT', 8001))
    print(f"🌐 Server running at: http://localhost:{port}")
    print("📱 Mobile test: Use your phone's browser with your computer's IP")
    print("🔧 Database: SQLite (nepsewa_local.db)")
    print("✨ Ready for development!")
    
    app.run(
        host='0.0.0.0',  # Allow external connections for mobile testing
        port=port,
        debug=True,      # Enable debug mode for development
        threaded=True    # Handle multiple requests
    )