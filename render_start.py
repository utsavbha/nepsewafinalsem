#!/usr/bin/env python3
"""
NepSewa Production Server for Render
Gradually adding full functionality
"""

import os
import sys
import urllib.parse as urlparse
from flask import Flask, jsonify, render_template

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask app with template and static folders
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.secret_key = "nepsewa_secret_key_2026"

# Database configuration
DB_CONFIG = {}

def setup_database_config():
    """Configure database connection for Render PostgreSQL"""
    global DB_CONFIG
    
    if os.environ.get('DATABASE_URL'):
        # Parse Render's DATABASE_URL for PostgreSQL
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        DB_CONFIG.update({
            'host': url.hostname,
            'port': url.port or 5432,
            'user': url.username,
            'password': url.password,
            'database': url.path[1:],  # Remove leading slash
            'ssl_context': {'check_hostname': False, 'verify_mode': 0}
        })
        print(f"✅ PostgreSQL configured: {url.hostname}:{url.port or 5432}")
        return True
    else:
        print("⚠️  No DATABASE_URL found")
        return False

def get_db():
    """Get database connection"""
    try:
        import pg8000
        conn = pg8000.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def test_database():
    """Test database connection"""
    try:
        conn = get_db()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
            conn.close()
            return True
    except Exception as e:
        print(f"Database test failed: {e}")
    return False

# Routes
@app.route("/")
def home():
    """Home page - try template first, fallback to simple HTML"""
    try:
        return render_template("nepsewa.html")
    except Exception as e:
        print(f"Template error: {e}")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>NepSewa - Service Marketplace</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .services { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
                .service-card { padding: 20px; border: 1px solid #ddd; border-radius: 8px; text-align: center; }
                .nav { margin-bottom: 20px; }
                .nav a { margin-right: 20px; color: #007bff; text-decoration: none; }
                .nav a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/services">Services</a>
                    <a href="/health">Health</a>
                    <a href="/login">Login</a>
                </div>
                <div class="header">
                    <h1>🏠 NepSewa - Service Marketplace</h1>
                    <p>Your trusted platform for home services in Nepal</p>
                </div>
                <div class="services">
                    <div class="service-card">
                        <h3>🧹 Home Cleaning</h3>
                        <p>Professional cleaning services</p>
                    </div>
                    <div class="service-card">
                        <h3>🔧 Plumbing</h3>
                        <p>Expert plumbing solutions</p>
                    </div>
                    <div class="service-card">
                        <h3>⚡ Electrical</h3>
                        <p>Safe electrical repairs</p>
                    </div>
                    <div class="service-card">
                        <h3>❄️ AC Service</h3>
                        <p>AC repair and maintenance</p>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <p><strong>Status:</strong> ✅ NepSewa is Live on Render!</p>
                </div>
            </div>
        </body>
        </html>
        """

@app.route("/services")
def services():
    """Services page"""
    try:
        return render_template("services.html")
    except Exception as e:
        return f"<h1>Services Page</h1><p>Template loading: {str(e)}</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/health")
def health():
    """Health check with database status"""
    db_status = "connected" if test_database() else "disconnected"
    db_configured = "yes" if DB_CONFIG else "no"
    
    return jsonify({
        "status": "healthy",
        "message": "NepSewa API is running on Render",
        "platform": "Render Cloud",
        "database": {
            "configured": db_configured,
            "status": db_status,
            "host": DB_CONFIG.get('host', 'not configured')
        },
        "features": {
            "templates": "checking...",
            "static_files": "checking...",
            "database": db_status
        }
    })

@app.route("/api/test")
def api_test():
    """API test endpoint"""
    return jsonify({
        "success": True,
        "message": "NepSewa API is working",
        "services": ["cleaning", "plumber", "electrician", "ac"],
        "database": "connected" if test_database() else "disconnected"
    })

def initialize_app():
    """Initialize the application for production"""
    print("🚀 NepSewa - Initializing production deployment")
    
    # Setup database
    db_configured = setup_database_config()
    
    if db_configured:
        db_working = test_database()
        print(f"✅ Database test: {'passed' if db_working else 'failed'}")
    
    # Set Flask configuration for production
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    
    print("✅ Application initialized successfully")
    return app

# Initialize the app
application = initialize_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8001))
    print(f"🌐 Starting NepSewa server on port {port}")
    application.run(host='0.0.0.0', port=port, debug=False)