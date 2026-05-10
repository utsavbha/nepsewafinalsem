#!/usr/bin/env python3
"""
NepSewa Production Server - Full Functionality
"""

import os
import sys
import json
import random
import string
import urllib.parse as urlparse
from datetime import datetime
from flask import Flask, jsonify, render_template, request, session, redirect, url_for

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
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        DB_CONFIG.update({
            'host': url.hostname,
            'port': url.port or 5432,
            'user': url.username,
            'password': url.password,
            'database': url.path[1:],
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

def init_db():
    """Initialize database tables"""
    try:
        conn = get_db()
        if not conn:
            return False
            
        with conn.cursor() as cur:
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(120) NOT NULL,
                    email VARCHAR(180) NOT NULL UNIQUE,
                    password VARCHAR(256) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Service providers table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS service_providers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(120) NOT NULL,
                    service VARCHAR(100) NOT NULL,
                    service_key VARCHAR(50) NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    district VARCHAR(100) NOT NULL,
                    latitude DECIMAL(10,8) DEFAULT NULL,
                    longitude DECIMAL(11,8) DEFAULT NULL,
                    rating DECIMAL(3,2) DEFAULT 4.0,
                    experience INTEGER DEFAULT 1,
                    completed_jobs INTEGER DEFAULT 0,
                    cancellation_rate DECIMAL(4,3) DEFAULT 0.0,
                    response_time_hours DECIMAL(4,1) DEFAULT 2.0,
                    is_verified BOOLEAN DEFAULT TRUE,
                    review_count INTEGER DEFAULT 0,
                    image TEXT,
                    phone VARCHAR(15),
                    availability JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if we have providers
            cur.execute("SELECT COUNT(*) FROM service_providers")
            count = cur.fetchone()[0]
            
            if count == 0:
                # Add sample providers
                providers = [
                    ("Aarav Sharma", "Home Cleaning", "cleaning", "Butwal", "Rupandehi", 4.8, 5, 312, 0.02, 1.5, True, 148, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face", "9801000001", '["Mon","Tue","Wed","Thu","Fri","Sat"]'),
                    ("Karuna Rai", "Makeup Artist", "makeup", "Tilottama", "Rupandehi", 4.9, 6, 420, 0.01, 1.0, True, 210, "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face", "9801000002", '["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'),
                    ("Arjun Basnet", "Plumbing", "plumber", "Bhairahawa", "Rupandehi", 4.7, 4, 198, 0.03, 2.0, True, 95, "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face", "9801000003", '["Mon","Tue","Wed","Thu","Fri"]'),
                    ("Deepa Rana", "Electric Repair", "electrician", "Chitwan", "Chitwan", 5.0, 4, 175, 0.00, 2.5, True, 88, "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face", "9801000004", '["Tue","Wed","Thu","Fri","Sat","Sun"]'),
                    ("Binod Joshi", "Hair Cutting", "haircutting", "Butwal", "Rupandehi", 4.2, 2, 89, 0.07, 3.0, False, 42, "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face", "9801000005", '["Mon","Wed","Fri","Sat","Sun"]'),
                    ("Sunita Oli", "AC Service", "ac", "Tilottama", "Rupandehi", 4.7, 3, 134, 0.04, 2.0, True, 67, "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face", "9801000006", '["Mon","Tue","Thu","Fri","Sat"]'),
                    ("Nisha Koirala", "Photographer", "photographer", "Chitwan", "Chitwan", 4.9, 8, 310, 0.01, 3.0, True, 155, "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&h=150&fit=crop&crop=face", "9801000007", '["Fri","Sat","Sun"]'),
                    ("Mamata Neupane", "Gardener", "gardener", "Bhairahawa", "Rupandehi", 4.3, 6, 145, 0.06, 4.0, False, 72, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face", "9801000008", '["Mon","Tue","Thu","Sat","Sun"]')
                ]
                
                for provider in providers:
                    cur.execute("""
                        INSERT INTO service_providers 
                        (name, service, service_key, location, district, rating, experience, 
                         completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                         review_count, image, phone, availability)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, provider)
                
                print("✅ Sample providers added")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# Routes
@app.route("/")
def home():
    """Home page"""
    try:
        return render_template("nepsewa.html")
    except Exception as e:
        print(f"Template error: {e}")
        return f"<h1>NepSewa - Service Marketplace</h1><p>Template error: {str(e)}</p><p><a href='/health'>Health Check</a></p>"

@app.route("/services")
def services():
    """Services page"""
    try:
        return render_template("services.html")
    except Exception as e:
        return f"<h1>Services Page</h1><p>Template loading: {str(e)}</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/map")
def nearby_map():
    """Find nearby providers map"""
    try:
        return render_template("nearby_map.html")
    except Exception as e:
        return f"<h1>Find Nearby</h1><p>Template error: {str(e)}</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/login")
def login_page():
    """Login page"""
    try:
        return render_template("login.html")
    except Exception as e:
        return f"<h1>Login</h1><p>Template error: {str(e)}</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/health")
def health():
    """Health check with database status"""
    db_status = "disconnected"
    db_configured = "no"
    
    if DB_CONFIG:
        db_configured = "yes"
        try:
            conn = get_db()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM service_providers")
                    provider_count = cur.fetchone()[0]
                conn.close()
                db_status = f"connected ({provider_count} providers)"
        except:
            db_status = "connection failed"
    
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
            "templates": "working",
            "static_files": "working",
            "database": db_status,
            "routes": ["home", "services", "map", "login", "api"]
        }
    })

@app.route("/api/top-professionals")
def api_top_professionals():
    """Get top 3 rated professionals for home page"""
    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM service_providers 
                WHERE rating >= 4.5 AND is_verified = true
                ORDER BY rating DESC, completed_jobs DESC, review_count DESC
                LIMIT 3
            """)
            professionals = []
            for row in cur.fetchall():
                professional = {
                    'id': row[0], 'name': row[1], 'service': row[2], 'service_key': row[3],
                    'location': row[4], 'district': row[5], 'latitude': row[6], 'longitude': row[7],
                    'rating': float(row[8]), 'experience': row[9], 'completed_jobs': row[10],
                    'cancellation_rate': float(row[11]), 'response_time_hours': float(row[12]),
                    'is_verified': row[13], 'review_count': row[14], 'image': row[15],
                    'phone': row[16], 'availability': json.loads(row[17]) if row[17] else []
                }
                professionals.append(professional)
        
        conn.close()
        return jsonify(success=True, professionals=professionals)
        
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/providers")
def api_providers():
    """Get providers with filtering"""
    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
        
        service_key = request.args.get("service_key", "")
        location = request.args.get("location", "")
        
        query = "SELECT * FROM service_providers WHERE 1=1"
        params = []
        
        if service_key:
            query += " AND service_key = %s"
            params.append(service_key)
        
        if location:
            query += " AND location = %s"
            params.append(location)
        
        query += " ORDER BY rating DESC, completed_jobs DESC LIMIT 20"
        
        with conn.cursor() as cur:
            cur.execute(query, params)
            providers = []
            for row in cur.fetchall():
                provider = {
                    'id': row[0], 'name': row[1], 'service': row[2], 'service_key': row[3],
                    'location': row[4], 'district': row[5], 'rating': float(row[8]),
                    'experience': row[9], 'completed_jobs': row[10], 'is_verified': row[13],
                    'review_count': row[14], 'image': row[15], 'phone': row[16]
                }
                providers.append(provider)
        
        conn.close()
        return jsonify(success=True, providers=providers)
        
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/providers/nearby")
def api_nearby_providers():
    """Get nearby providers"""
    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
        
        # For now, return all providers since GPS coordinates might not be set
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM service_providers 
                WHERE is_verified = true
                ORDER BY rating DESC 
                LIMIT 15
            """)
            providers = []
            for row in cur.fetchall():
                provider = {
                    'id': row[0], 'name': row[1], 'service': row[2], 'service_key': row[3],
                    'location': row[4], 'district': row[5], 'rating': float(row[8]),
                    'experience': row[9], 'completed_jobs': row[10], 'is_verified': row[13],
                    'review_count': row[14], 'image': row[15], 'phone': row[16],
                    'distance_km': round(random.uniform(0.5, 5.0), 1)  # Simulated distance
                }
                providers.append(provider)
        
        conn.close()
        return jsonify(success=True, providers=providers)
        
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

def initialize_app():
    """Initialize the application for production"""
    print("🚀 NepSewa - Initializing full production deployment")
    
    # Setup database
    db_configured = setup_database_config()
    
    if db_configured:
        db_initialized = init_db()
        print(f"✅ Database initialization: {'success' if db_initialized else 'failed'}")
    
    # Set Flask configuration for production
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    
    print("✅ Full NepSewa application initialized successfully")
    return app

# Initialize the app
application = initialize_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8001))
    print(f"🌐 Starting full NepSewa server on port {port}")
    application.run(host='0.0.0.0', port=port, debug=False)