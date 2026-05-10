#!/usr/bin/env python3
"""
Render Deployment Startup Script for NepSewa
This script is optimized for Render's deployment environment
"""

import os
import sys
import pymysql
import urllib.parse as urlparse

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, init_db

def setup_database_config():
    """Configure database connection for Render"""
    from main import DB_CONFIG
    
    if os.environ.get('DATABASE_URL'):
        # Parse Render's DATABASE_URL
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        DB_CONFIG.update({
            'host': url.hostname,
            'port': url.port or 3306,
            'user': url.username,
            'password': url.password,
            'database': url.path[1:],  # Remove leading slash
            'autocommit': True,
            'cursorclass': pymysql.cursors.DictCursor
        })
        print(f"✅ Database configured: {url.hostname}:{url.port or 3306}")
    else:
        print("⚠️  No DATABASE_URL found, using default config")

def initialize_app():
    """Initialize the application for production"""
    print("🚀 NepSewa - Initializing for Render deployment")
    
    # Setup database
    setup_database_config()
    
    # Initialize database tables
    try:
        init_db()
        print("✅ Database tables initialized")
    except Exception as e:
        print(f"⚠️  Database init warning: {e}")
        print("   (Tables might already exist)")
    
    # Set Flask configuration for production
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    
    print("✅ Application initialized successfully")
    return app

# Initialize the app when this module is imported
application = initialize_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8001))
    print(f"🌐 Starting server on port {port}")
    application.run(host='0.0.0.0', port=port, debug=False)