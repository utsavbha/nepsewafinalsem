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
import hmac
import hashlib
import base64
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
        # Try PostgreSQL first (for production)
        if DB_CONFIG and DB_CONFIG.get('host'):
            import pg8000
            conn = pg8000.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                ssl_context=True
            )
            conn.autocommit = True
            return conn
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        
    # Fallback to SQLite for local development
    try:
        import sqlite3
        conn = sqlite3.connect('nepsewa_local.db')
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except Exception as e:
        print(f"SQLite connection failed: {e}")
        return None

def init_db():
    """Initialize database tables"""
    try:
        conn = get_db()
        if not conn:
            return False
        
        # Detect database type
        is_sqlite = hasattr(conn, 'row_factory')
        
        if is_sqlite:
            cursor = conn.cursor()
        else:
            cursor = conn.cursor()
            
        # Users table
        if is_sqlite:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(120) NOT NULL,
                    email VARCHAR(180) NOT NULL UNIQUE,
                    password VARCHAR(256) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Service providers table
        if is_sqlite:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS service_providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    service TEXT NOT NULL,
                    service_key TEXT NOT NULL,
                    location TEXT NOT NULL,
                    district TEXT NOT NULL,
                    latitude REAL DEFAULT NULL,
                    longitude REAL DEFAULT NULL,
                    rating REAL DEFAULT 4.0,
                    experience INTEGER DEFAULT 1,
                    completed_jobs INTEGER DEFAULT 0,
                    cancellation_rate REAL DEFAULT 0.0,
                    response_time_hours REAL DEFAULT 2.0,
                    is_verified INTEGER DEFAULT 1,
                    review_count INTEGER DEFAULT 0,
                    image TEXT,
                    phone TEXT,
                    availability TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cursor.execute("""
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
        cursor.execute("SELECT COUNT(*) FROM service_providers")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📊 Database is empty, adding sample providers...")
            # Add sample providers for local development
            add_sample_providers_local(cursor, is_sqlite)
            print("✅ Sample providers added")
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

def add_sample_providers_local(cursor, is_sqlite):
    """Add sample providers for local development"""
    providers = [
        ("Aarav Sharma", "Home Cleaning", "cleaning", "Butwal", "Rupandehi", 27.7012, 83.4523, 4.8, 5, 312, 0.02, 1.5, 1, 148, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face", "9801000001", '["Mon","Tue","Wed","Thu","Fri","Sat"]'),
        ("Karuna Rai", "Makeup Artist", "makeup", "Tilottama", "Rupandehi", 27.7189, 83.4287, 4.9, 6, 420, 0.01, 1.0, 1, 210, "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face", "9801000002", '["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'),
        ("Arjun Basnet", "Plumbing", "plumber", "Bhairahawa", "Rupandehi", 27.5095, 83.4534, 4.7, 4, 198, 0.03, 2.0, 1, 95, "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face", "9801000003", '["Mon","Tue","Wed","Thu","Fri"]'),
        ("Deepa Rana", "Electric Repair", "electrician", "Chitwan", "Chitwan", 27.5278, 84.3567, 5.0, 4, 175, 0.00, 2.5, 1, 88, "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face", "9801000004", '["Tue","Wed","Thu","Fri","Sat","Sun"]'),
        ("Binod Joshi", "Hair Cutting", "haircutting", "Butwal", "Rupandehi", 27.6987, 83.4478, 4.2, 2, 89, 0.07, 3.0, 0, 42, "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face", "9801000005", '["Mon","Wed","Fri","Sat","Sun"]'),
        ("Sunita Oli", "AC Service", "ac", "Tilottama", "Rupandehi", 27.7156, 83.4298, 4.7, 3, 134, 0.04, 2.0, 1, 67, "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face", "9801000006", '["Mon","Tue","Thu","Fri","Sat"]'),
        ("Nisha Koirala", "Photographer", "photographer", "Chitwan", "Chitwan", 27.5267, 84.3589, 4.9, 8, 310, 0.01, 3.0, 1, 155, "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&h=150&fit=crop&crop=face", "9801000007", '["Fri","Sat","Sun"]'),
        ("Mamata Neupane", "Gardener", "gardener", "Bhairahawa", "Rupandehi", 27.5101, 83.4456, 4.3, 6, 145, 0.06, 4.0, 0, 72, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face", "9801000008", '["Mon","Tue","Thu","Sat","Sun"]')
    ]
    
    for provider in providers:
        if is_sqlite:
            cursor.execute("""
                INSERT INTO service_providers 
                (name, service, service_key, location, district, latitude, longitude, rating, experience, 
                 completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                 review_count, image, phone, availability)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, provider)
        else:
            cursor.execute("""
                INSERT INTO service_providers 
                (name, service, service_key, location, district, latitude, longitude, rating, experience, 
                 completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                 review_count, image, phone, availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, provider)

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

@app.route("/admin/test")
def admin_test():
    """Admin test page for database population"""
    return render_template("admin_test.html")

@app.route("/api/status")
def api_status():
    """Comprehensive status check"""
    try:
        status = {
            "app": "NepSewa",
            "version": "2.0",
            "platform": "Render Cloud",
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "database": {
                "configured": bool(DB_CONFIG),
                "connected": False,
                "provider_count": 0,
                "tables": []
            },
            "features": {
                "templates": True,
                "static_files": True,
                "authentication": True,
                "payments": True,
                "booking": True,
                "provider_registration": True
            },
            "endpoints": {
                "home": "/",
                "services": "/services",
                "map": "/map",
                "login": "/login",
                "api_health": "/health",
                "api_providers": "/api/providers",
                "api_services": "/api/services",
                "api_top_professionals": "/api/top-professionals"
            }
        }
        
        # Test database connection
        try:
            conn = get_db()
            if conn:
                status["database"]["connected"] = True
                
                with conn.cursor() as cur:
                    # Get provider count
                    cur.execute("SELECT COUNT(*) FROM service_providers")
                    status["database"]["provider_count"] = cur.fetchone()[0]
                    
                    # Get table list
                    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                    status["database"]["tables"] = [row[0] for row in cur.fetchall()]
                
                conn.close()
        except Exception as e:
            status["database"]["error"] = str(e)
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            "app": "NepSewa",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 500

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
        
        # Detect database type
        is_sqlite = hasattr(conn, 'row_factory')
        
        if is_sqlite:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM service_providers 
                WHERE rating >= 4.5 AND is_verified = 1
                ORDER BY rating DESC, completed_jobs DESC, review_count DESC
                LIMIT 3
            """)
            rows = cursor.fetchall()
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM service_providers 
                WHERE rating >= 4.5 AND is_verified = true
                ORDER BY rating DESC, completed_jobs DESC, review_count DESC
                LIMIT 3
            """)
            rows = cursor.fetchall()
        
        professionals = []
        for row in rows:
            if is_sqlite:
                # SQLite row access by index
                professional = {
                    'id': row[0], 'name': row[1], 'service': row[2], 'service_key': row[3],
                    'location': row[4], 'district': row[5], 'latitude': row[6], 'longitude': row[7],
                    'rating': float(row[8]), 'experience': row[9], 'completed_jobs': row[10],
                    'cancellation_rate': float(row[11]), 'response_time_hours': float(row[12]),
                    'is_verified': bool(row[13]), 'review_count': row[14], 'image': row[15],
                    'phone': row[16], 'availability': row[17] if row[17] else '[]'
                }
            else:
                # PostgreSQL row access by index
                professional = {
                    'id': row[0], 'name': row[1], 'service': row[2], 'service_key': row[3],
                    'location': row[4], 'district': row[5], 'latitude': row[6], 'longitude': row[7],
                    'rating': float(row[8]), 'experience': row[9], 'completed_jobs': row[10],
                    'cancellation_rate': float(row[11]), 'response_time_hours': float(row[12]),
                    'is_verified': row[13], 'review_count': row[14], 'image': row[15],
                    'phone': row[16], 'availability': row[17] if row[17] else '[]'
                }
            
            # Parse availability if it's a string
            if isinstance(professional['availability'], str):
                try:
                    import json
                    professional['availability'] = json.loads(professional['availability'])
                except:
                    professional['availability'] = []
            
            professionals.append(professional)
        
        conn.close()
        print(f"✅ Found {len(professionals)} top professionals")
        return jsonify(success=True, professionals=professionals)
        
    except Exception as e:
        print(f"❌ Top professionals error: {e}")
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

@app.route("/api/services")
def api_services():
    """Get all available service categories"""
    try:
        # Return the service categories that match your database
        services = [
            {
                "service_key": "cleaning",
                "service_name": "Home Cleaning",
                "provider_count": 3,
                "avg_rating": 4.7,
                "title": "Home Cleaning",
                "price": "Rs. 500 / Hour",
                "image": "https://sunflowermaids.com/wp-content/uploads/2021/08/Signs-of-a-Bad-Cleaning-Lady.jpg",
                "description": "Kitchens, bathrooms, bedrooms and living rooms cleaned thoroughly."
            },
            {
                "service_key": "plumber",
                "service_name": "Plumbing",
                "provider_count": 2,
                "avg_rating": 4.7,
                "title": "Plumber Service",
                "price": "Rs. 500 / Hour",
                "image": "https://nnps.com.np/wp-content/uploads/2023/06/imgs-1.jpg",
                "description": "Our plumbers fix leaking taps, blocked drains, broken pipes and bathroom fittings."
            },
            {
                "service_key": "electrician",
                "service_name": "Electric Repair",
                "provider_count": 2,
                "avg_rating": 4.8,
                "title": "Electrician Service",
                "price": "Rs. 500 / Hour",
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTXwC_BznDpwyR2eeQpC7mAQTTisL33B2Mt3g&s",
                "description": "Switch repairs, fan and light installations, power socket fitting, and circuit troubleshooting."
            },
            {
                "service_key": "ac",
                "service_name": "AC Service",
                "provider_count": 1,
                "avg_rating": 4.7,
                "title": "AC Repair & Service",
                "price": "Rs. 500 / Hour",
                "image": "https://clareservices.com/wp-content/uploads/2020/07/air-conditioning-repair-service-hyderabad.jpg",
                "description": "Regular servicing, filter cleaning, gas refilling and fault repairs for all major AC brands."
            },
            {
                "service_key": "haircutting",
                "service_name": "Hair Cutting",
                "provider_count": 1,
                "avg_rating": 4.2,
                "title": "Hair Cutting",
                "price": "Rs. 200 / Person",
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBOJdrtttgPWstF4HcMoxCwE8pU2dNwZEYQg&s",
                "description": "Professional haircut at home. Our barbers bring all their own tools."
            },
            {
                "service_key": "makeup",
                "service_name": "Makeup Artist",
                "provider_count": 1,
                "avg_rating": 4.9,
                "title": "Makeup Artist",
                "price": "Rs. 500 / Hour",
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRaaYzEvMXuqWZ5Hp5Q14B9vqRFu5fQvlfBEA&s",
                "description": "Home visits for weddings, parties, photoshoots and daily events."
            },
            {
                "service_key": "photographer",
                "service_name": "Photographer",
                "provider_count": 1,
                "avg_rating": 4.9,
                "title": "Photographer",
                "price": "Rs. 500 / Hour",
                "image": "https://img.freepik.com/free-photo/young-stylish-photographer-holds-professional-camera-taking-photos_8353-6506.jpg",
                "description": "Family events, product shoots, birthdays, ceremonies. Camera and lighting provided."
            },
            {
                "service_key": "gardener",
                "service_name": "Gardener",
                "provider_count": 1,
                "avg_rating": 4.3,
                "title": "Gardener Service",
                "price": "Rs. 1,000 / Day",
                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTC99OjYEYoOEna34FkVD741eZRu7AUVtSO3w&s",
                "description": "Lawn mowing, plant trimming, weeding, watering and basic garden maintenance."
            }
        ]
        
        return jsonify(success=True, services=services)
        
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/add-comprehensive-providers", methods=["POST"])
def add_comprehensive_providers():
    """Add comprehensive set of providers with GPS coordinates"""
    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
        
        # Clear existing providers first
        with conn.cursor() as cur:
            cur.execute("DELETE FROM service_providers")
            
            # Comprehensive provider data with GPS coordinates
            providers = [
                # Home Cleaning Providers
                ("Aarav Sharma", "Home Cleaning", "cleaning", "Butwal", "Rupandehi", 27.7012, 83.4523, 4.8, 5, 312, 0.02, 1.5, True, 148, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face", "9801000001"),
                ("Sita Lama", "Home Cleaning", "cleaning", "Tilottama", "Rupandehi", 27.7189, 83.4287, 4.9, 6, 420, 0.01, 1.0, True, 210, "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face", "9801000002"),
                ("Maya Gurung", "Home Cleaning", "cleaning", "Bhairahawa", "Rupandehi", 27.5095, 83.4534, 4.3, 2, 67, 0.08, 4.0, False, 34, "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face", "9801000003"),
                
                # Plumbing Providers
                ("Arjun Basnet", "Plumbing", "plumber", "Butwal", "Rupandehi", 27.6987, 83.4478, 4.7, 4, 198, 0.03, 2.0, True, 95, "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face", "9801000004"),
                ("Hari Sharma", "Plumbing", "plumber", "Tilottama", "Rupandehi", 27.7234, 83.4312, 4.5, 3, 156, 0.05, 2.5, True, 78, "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face", "9801000005"),
                ("Raju Maharjan", "Plumbing", "plumber", "Chitwan", "Chitwan", 27.5278, 84.3567, 4.6, 6, 234, 0.02, 2.0, True, 117, "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face", "9801000006"),
                
                # Electrician Providers
                ("Deepa Rana", "Electric Repair", "electrician", "Bhairahawa", "Rupandehi", 27.5067, 83.4501, 5.0, 4, 175, 0.00, 2.5, True, 88, "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&h=150&fit=crop&crop=face", "9801000007"),
                ("Ram Bahadur", "Electric Repair", "electrician", "Butwal", "Rupandehi", 27.7023, 83.4489, 4.8, 5, 312, 0.02, 1.5, True, 148, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face", "9801000008"),
                ("Bikash Tamang", "Electric Repair", "electrician", "Chitwan", "Chitwan", 27.5312, 84.3523, 4.4, 3, 123, 0.05, 3.0, False, 61, "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face", "9801000009"),
                
                # AC Service Providers
                ("Sunita Oli", "AC Service", "ac", "Tilottama", "Rupandehi", 27.7156, 83.4298, 4.7, 3, 134, 0.04, 2.0, True, 67, "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face", "9801000010"),
                ("Binod KC", "AC Service", "ac", "Butwal", "Rupandehi", 27.6998, 83.4512, 4.5, 4, 220, 0.03, 2.0, True, 110, "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face", "9801000011"),
                ("Nabin Karki", "AC Service", "ac", "Bhairahawa", "Rupandehi", 27.5089, 83.4487, 4.6, 5, 178, 0.03, 2.0, True, 89, "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face", "9801000012"),
                
                # Hair Cutting Providers
                ("Binod Joshi", "Hair Cutting", "haircutting", "Butwal", "Rupandehi", 27.7034, 83.4456, 4.2, 2, 89, 0.07, 3.0, False, 42, "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face", "9801000013"),
                ("Ramesh Tamang", "Hair Cutting", "haircutting", "Tilottama", "Rupandehi", 27.7201, 83.4334, 4.5, 4, 145, 0.04, 2.5, True, 73, "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face", "9801000014"),
                ("Sabita Chhetri", "Hair Cutting", "haircutting", "Chitwan", "Chitwan", 27.5289, 84.3578, 4.8, 7, 289, 0.02, 1.5, True, 145, "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=150&h=150&fit=crop&crop=face", "9801000015"),
                
                # Makeup Artist Providers
                ("Karuna Rai", "Makeup Artist", "makeup", "Butwal", "Rupandehi", 27.6976, 83.4534, 4.9, 6, 420, 0.01, 1.0, True, 210, "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=150&h=150&fit=crop&crop=face", "9801000016"),
                ("Gita KC", "Makeup Artist", "makeup", "Tilottama", "Rupandehi", 27.7178, 83.4267, 5.0, 4, 175, 0.00, 2.5, True, 88, "https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?w=150&h=150&fit=crop&crop=face", "9801000017"),
                ("Priya Shrestha", "Makeup Artist", "makeup", "Bhairahawa", "Rupandehi", 27.5078, 83.4523, 4.8, 5, 260, 0.02, 2.0, True, 130, "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=150&h=150&fit=crop&crop=face", "9801000018"),
                
                # Photographer Providers
                ("Nisha Koirala", "Photographer", "photographer", "Chitwan", "Chitwan", 27.5267, 84.3589, 4.9, 8, 310, 0.01, 3.0, True, 155, "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=150&h=150&fit=crop&crop=face", "9801000019"),
                ("Anil Shakya", "Photographer", "photographer", "Butwal", "Rupandehi", 27.7045, 83.4467, 4.7, 6, 234, 0.02, 2.5, True, 117, "https://images.unsplash.com/photo-1566492031773-4f4e44671d66?w=150&h=150&fit=crop&crop=face", "9801000020"),
                ("Puja Manandhar", "Photographer", "photographer", "Tilottama", "Rupandehi", 27.7167, 83.4289, 4.4, 3, 123, 0.04, 3.0, True, 62, "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?w=150&h=150&fit=crop&crop=face", "9801000021"),
                
                # Gardener Providers
                ("Mamata Neupane", "Gardener", "gardener", "Bhairahawa", "Rupandehi", 27.5101, 83.4456, 4.3, 6, 145, 0.06, 4.0, False, 72, "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=150&h=150&fit=crop&crop=face", "9801000022"),
                ("Rajesh Pandey", "Gardener", "gardener", "Butwal", "Rupandehi", 27.6989, 83.4501, 4.4, 5, 123, 0.05, 3.0, True, 62, "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150&h=150&fit=crop&crop=face", "9801000023"),
                ("Dilip Tharu", "Gardener", "gardener", "Chitwan", "Chitwan", 27.5301, 84.3534, 4.2, 4, 98, 0.07, 3.5, False, 49, "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face", "9801000024"),
                
                # Maid Service Providers
                ("Anita Thapa", "Maid Service", "maid", "Tilottama", "Rupandehi", 27.7145, 83.4323, 4.6, 7, 380, 0.02, 1.5, True, 190, "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=150&h=150&fit=crop&crop=face", "9801000025"),
                ("Devi Pun", "Maid Service", "maid", "Butwal", "Rupandehi", 27.7056, 83.4478, 4.2, 3, 89, 0.07, 3.5, False, 45, "https://images.unsplash.com/photo-1520813792240-56fc4a3765a7?w=150&h=150&fit=crop&crop=face", "9801000026"),
                ("Bishnu Ghale", "Maid Service", "maid", "Bhairahawa", "Rupandehi", 27.5112, 83.4467, 4.8, 9, 567, 0.01, 1.0, True, 284, "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=150&h=150&fit=crop&crop=face", "9801000027"),
                
                # Technician Service Providers
                ("Deepak Gurung", "Technician Service", "technician", "Chitwan", "Chitwan", 27.5323, 84.3545, 4.4, 3, 112, 0.05, 3.5, False, 55, "https://images.unsplash.com/photo-1499952127939-9bbf5af6c51c?w=150&h=150&fit=crop&crop=face", "9801000028"),
                ("Gopal Adhikari", "Technician Service", "technician", "Butwal", "Rupandehi", 27.7067, 83.4489, 4.7, 6, 234, 0.02, 1.5, True, 117, "https://images.unsplash.com/photo-1496345875659-11f7dd282d1d?w=150&h=150&fit=crop&crop=face", "9801000029"),
                ("Mina Oli", "Technician Service", "technician", "Tilottama", "Rupandehi", 27.7189, 83.4301, 4.1, 2, 56, 0.08, 4.0, False, 28, "https://images.unsplash.com/photo-1521119989659-a83eee488004?w=150&h=150&fit=crop&crop=face", "9801000030")
            ]
            
            for provider in providers:
                cur.execute("""
                    INSERT INTO service_providers 
                    (name, service, service_key, location, district, latitude, longitude, rating, experience, 
                     completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                     review_count, image, phone, availability)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, provider + ('["Mon","Tue","Wed","Thu","Fri","Sat"]',))
            
            # Get final count
            cur.execute("SELECT COUNT(*) FROM service_providers")
            final_count = cur.fetchone()[0]
        
        conn.close()
        return jsonify(success=True, message=f"Added {final_count} comprehensive providers with GPS coordinates!")
        
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/add-sample-data", methods=["POST"])
def add_sample_data():
    """Add sample data if database is empty"""
    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
        
        # Check if we already have providers
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM service_providers")
            count = cur.fetchone()[0]
            
            if count > 0:
                return jsonify(success=True, message=f"Already have {count} providers")
            
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
            
            # Get final count
            cur.execute("SELECT COUNT(*) FROM service_providers")
            final_count = cur.fetchone()[0]
        
        conn.close()
        return jsonify(success=True, message=f"Added {final_count} providers successfully!")
        
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

# ─────────────────────────────────────────────
# ESEWA PAYMENT INTEGRATION
# ─────────────────────────────────────────────
ESEWA_MERCHANT_CODE = "EPAYTEST"
ESEWA_SECRET_KEY = "8gBm/:&EnhH.1/q"
ESEWA_BASE_URL = "https://rc-epay.esewa.com.np"

SERVICE_PRICES = {
    "cleaning": 500, "plumber": 500, "electrician": 500, "ac": 500,
    "haircutting": 200, "makeup": 500, "photographer": 500, "gardener": 1000,
    "maid": 500, "technician": 300
}

@app.route("/api/esewa/initiate", methods=["POST"])
def esewa_initiate():
    """Initiate eSewa payment"""
    try:
        data = request.get_json(silent=True) or {}
        booking_id = data.get("booking_id")
        
        if not booking_id:
            return jsonify(success=False, message="Booking ID required")
        
        # Get service price (default to 500 if not found)
        service_key = currentServiceType if 'currentServiceType' in globals() else 'cleaning'
        amount = SERVICE_PRICES.get(service_key, 500)
        
        # eSewa payment parameters
        transaction_uuid = booking_id
        product_code = ESEWA_MERCHANT_CODE
        
        # Create signature
        message = f"total_amount={amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        signature = base64.b64encode(
            hmac.new(ESEWA_SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()
        
        return jsonify({
            "success": True,
            "esewa_url": f"{ESEWA_BASE_URL}/api/epay/main/v2/form",
            "amount": str(amount),
            "transaction_uuid": transaction_uuid,
            "product_code": product_code,
            "merchant_code": ESEWA_MERCHANT_CODE,
            "signature": signature,
            "success_url": f"{request.host_url}payment/success",
            "failure_url": f"{request.host_url}payment/failed"
        })
        
    except Exception as e:
        return jsonify(success=False, message=f"Payment initiation failed: {str(e)}")

@app.route("/api/payment/cash", methods=["POST"])
def payment_cash():
    """Handle cash payment"""
    try:
        data = request.get_json(silent=True) or {}
        booking_id = data.get("booking_id")
        
        if not booking_id:
            return jsonify(success=False, message="Booking ID required")
        
        # Update order status (you can implement order storage later)
        return jsonify(success=True, message="Cash payment confirmed")
        
    except Exception as e:
        return jsonify(success=False, message=f"Payment processing failed: {str(e)}")

@app.route("/api/orders/update", methods=["POST"])
def update_order():
    """Update order status"""
    try:
        data = request.get_json(silent=True) or {}
        booking_id = data.get("booking_id")
        status = data.get("status", "confirmed")
        
        if not booking_id:
            return jsonify(success=False, message="Booking ID required")
        
        # For now, just return success (you can implement order storage later)
        return jsonify(success=True, message=f"Order {booking_id} updated to {status}")
        
    except Exception as e:
        return jsonify(success=False, message=f"Order update failed: {str(e)}")

@app.route("/payment/success")
def payment_success():
    """eSewa payment success callback"""
    try:
        return render_template("payment_success.html")
    except Exception as e:
        return f"<h1>Payment Successful!</h1><p>Your booking has been confirmed.</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/payment/failed")
def payment_failed():
    """eSewa payment failure callback"""
    try:
        return render_template("payment_failed.html")
    except Exception as e:
        return f"<h1>Payment Failed</h1><p>Please try again or contact support.</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/api/debug/db")
def debug_database():
    """Debug database connection"""
    try:
        if not DB_CONFIG:
            return jsonify({"error": "No database configuration", "config": "missing"})
        
        # Test connection
        conn = get_db()
        if not conn:
            return jsonify({"error": "Cannot connect to database", "config": DB_CONFIG.get('host', 'unknown')})
        
        # Test query
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            
            # Check tables
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in cur.fetchall()]
            
            # Check provider count if table exists
            provider_count = 0
            if 'service_providers' in tables:
                cur.execute("SELECT COUNT(*) FROM service_providers")
                provider_count = cur.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "database_version": version,
            "tables": tables,
            "provider_count": provider_count,
            "config_host": DB_CONFIG.get('host', 'unknown')
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "type": type(e).__name__})

@app.route("/provider/register")
def provider_register_page():
    """Provider registration page"""
    try:
        return render_template("provider_register.html")
    except Exception as e:
        return f"<h1>Become a Provider</h1><p>Template error: {str(e)}</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/register-provider")
def register_provider_page():
    """Provider registration page (alternative route)"""
    try:
        return render_template("register_provider.html")
    except Exception as e:
        return f"<h1>Register as Provider</h1><p>Template error: {str(e)}</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/provider/login")
def provider_login_page():
    """Provider login page"""
    try:
        return render_template("provider_login.html")
    except Exception as e:
        return f"<h1>Provider Login</h1><p>Template error: {str(e)}</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/api/register-provider", methods=["POST"])
def register_provider():
    """Register a new service provider"""
    try:
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        phone = (data.get("phone") or "").strip()
        service = data.get("service")
        location = data.get("location")
        experience = int(data.get("experience", 1))

        if not all([name, phone, service, location]):
            return jsonify(success=False, message="All required fields must be filled")

        # Map service names to keys
        service_mapping = {
            "Home Cleaning": {"key": "cleaning", "name": "Home Cleaning"},
            "Plumbing": {"key": "plumber", "name": "Plumbing"},
            "Electric Repair": {"key": "electrician", "name": "Electric Repair"},
            "AC Service": {"key": "ac", "name": "AC Service"},
            "Maid Service": {"key": "maid", "name": "Maid Service"},
            "Technician Service": {"key": "technician", "name": "Technician Service"},
            "Hair Cutting": {"key": "haircutting", "name": "Hair Cutting"},
            "Gardening": {"key": "gardener", "name": "Gardener"},
            "Makeup Artist": {"key": "makeup", "name": "Makeup Artist"},
            "Photography": {"key": "photographer", "name": "Photographer"}
        }

        if service not in service_mapping:
            return jsonify(success=False, message="Invalid service selected")

        service_info = service_mapping[service]

        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")

        with conn.cursor() as cur:
            # Check if phone already exists
            cur.execute("SELECT id FROM service_providers WHERE phone = %s", (phone,))
            if cur.fetchone():
                return jsonify(success=False, message="Phone number already registered")

            # Insert new provider
            cur.execute("""
                INSERT INTO service_providers 
                (name, service, service_key, location, district, rating, experience, 
                 completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                 review_count, image, phone, availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                name, service_info["name"], service_info["key"], location, location,
                3.5, experience, 0, 0.0, 4.0, False, 0,
                "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
                phone, '["Mon","Tue","Wed","Thu","Fri","Sat"]'
            ))

        conn.close()
        return jsonify(success=True, message="Registration successful! Please wait for admin approval.")

    except Exception as e:
        return jsonify(success=False, message=f"Registration failed: {str(e)}")

@app.route("/profile")
def profile_page():
    """Profile page"""
    if not session.get("user_id"):
        return redirect("/login?redirect=/profile")
    try:
        return render_template("profile.html")
    except Exception as e:
        return f"<h1>Profile Page</h1><p>Template error: {str(e)}</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/logout")
def logout():
    """Logout user"""
    session.clear()
    return redirect("/")

@app.route("/orders")
def orders_page():
    """Orders page"""
    if not session.get("user_id"):
        return redirect("/login?redirect=/orders")
    try:
        return render_template("orders.html")
    except Exception as e:
        return f"<h1>My Orders</h1><p>Template error: {str(e)}</p><p><a href='/'>← Back to Home</a></p>"

@app.route("/api/providers/nearby")
def api_nearby_providers():
    """Get nearby providers with GPS coordinates"""
    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
        
        # Get user location from query parameters (optional)
        user_lat = request.args.get('lat', type=float)
        user_lng = request.args.get('lng', type=float)
        
        with conn.cursor() as cur:
            # Get all providers with GPS coordinates
            cur.execute("""
                SELECT id, name, service, service_key, location, district, 
                       latitude, longitude, rating, experience, completed_jobs, 
                       is_verified, review_count, image, phone
                FROM service_providers 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                ORDER BY rating DESC, completed_jobs DESC
                LIMIT 20
            """)
            
            providers = []
            for row in cur.fetchall():
                provider = {
                    'id': row[0], 'name': row[1], 'service': row[2], 'service_key': row[3],
                    'location': row[4], 'district': row[5], 'latitude': float(row[6]), 
                    'longitude': float(row[7]), 'rating': float(row[8]), 'experience': row[9], 
                    'completed_jobs': row[10], 'is_verified': row[11], 'review_count': row[12], 
                    'image': row[13], 'phone': row[14]
                }
                
                # Calculate distance if user location provided
                if user_lat and user_lng:
                    import math
                    # Haversine formula for distance calculation
                    lat1, lon1 = math.radians(user_lat), math.radians(user_lng)
                    lat2, lon2 = math.radians(provider['latitude']), math.radians(provider['longitude'])
                    
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                    c = 2 * math.asin(math.sqrt(a))
                    distance_km = 6371 * c  # Earth's radius in km
                    
                    provider['distance_km'] = round(distance_km, 1)
                else:
                    # Simulate distance for demo
                    provider['distance_km'] = round(random.uniform(0.5, 8.0), 1)
                
                providers.append(provider)
            
            # Sort by distance if user location provided
            if user_lat and user_lng:
                providers.sort(key=lambda x: x['distance_km'])
        
        conn.close()
        return jsonify(success=True, providers=providers, count=len(providers))
        
    except Exception as e:
        print(f"Nearby providers error: {e}")
        return jsonify(success=False, message=f"Error: {str(e)}")

# ─────────────────────────────────────────────
# AUTH API
# ─────────────────────────────────────────────
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not name or not email or not password:
        return jsonify(success=False, message="All fields are required")
    if len(password) < 6:
        return jsonify(success=False, message="Password must be at least 6 characters")

    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
            
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                return jsonify(success=False, message="Email already registered")
            
            from werkzeug.security import generate_password_hash
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, generate_password_hash(password))
            )
        conn.close()
        return jsonify(success=True, message="Account created successfully")
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify(success=False, message="All fields are required")

    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
            
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, password, created_at FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

        if not user:
            return jsonify(success=False, message="Invalid email or password")
            
        from werkzeug.security import check_password_hash
        if not check_password_hash(user[3], password):
            return jsonify(success=False, message="Invalid email or password")

        session["user_id"] = user[0]
        session["user_name"] = user[1]
        session["user_email"] = user[2]
        
        redirect_url = data.get("redirect_url", "/profile")
        conn.close()
        return jsonify(success=True, message="Login successful", redirect_url=redirect_url)
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/me")
def api_me():
    if not session.get("user_id"):
        return jsonify(success=False, message="Not logged in"), 401

    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
            
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, created_at FROM users WHERE id=%s",
                (session["user_id"],)
            )
            user = cur.fetchone()

        if not user:
            session.clear()
            return jsonify(success=False, message="User not found"), 404

        # Simulate bookings for now
        bookings = []

        conn.close()
        return jsonify(
            success=True,
            user=dict(
                id=user[0],
                name=user[1],
                email=user[2],
                member_since=str(user[3])[:10],
                total_bookings=len(bookings),
                bookings=bookings,
                initials="".join(w[0].upper() for w in user[1].split()[:2])
            )
        )
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

# ─────────────────────────────────────────────
# PROVIDER AUTH API
# ─────────────────────────────────────────────
@app.route("/api/provider/login", methods=["POST"])
def provider_login():
    """Provider login API"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify(success=False, message="All fields are required")

    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
            
        with conn.cursor() as cur:
            # Check if provider exists in service_providers table
            cur.execute("SELECT id, name, phone FROM service_providers WHERE phone = %s", (email,))
            provider = cur.fetchone()

        if not provider:
            return jsonify(success=False, message="Provider not found. Please register first.")
            
        # For now, accept any password (you can implement proper password hashing later)
        # In production, you should hash passwords and verify them properly
        
        session["provider_id"] = provider[0]
        session["provider_name"] = provider[1]
        session["provider_phone"] = provider[2]
        
        conn.close()
        return jsonify(success=True, message="Login successful", redirect_url="/provider/dashboard")
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/provider/me")
def api_provider_me():
    """Get current provider info"""
    if not session.get("provider_id"):
        return jsonify(success=False, message="Not logged in"), 401

    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
            
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, service, location, rating, experience, completed_jobs, is_verified, review_count, image, phone FROM service_providers WHERE id=%s",
                (session["provider_id"],)
            )
            provider = cur.fetchone()

        if not provider:
            session.clear()
            return jsonify(success=False, message="Provider not found"), 404

        conn.close()
        return jsonify(
            success=True,
            provider=dict(
                id=provider[0],
                name=provider[1],
                service=provider[2],
                location=provider[3],
                rating=float(provider[4]),
                experience=provider[5],
                completed_jobs=provider[6],
                is_verified=provider[7],
                review_count=provider[8],
                image=provider[9],
                phone=provider[10],
                initials="".join(w[0].upper() for w in provider[1].split()[:2])
            )
        )
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/provider/dashboard")
def provider_dashboard():
    """Provider dashboard page"""
    if not session.get("provider_id"):
        return redirect("/provider/login")
    try:
        return render_template("provider_dashboard.html")
    except Exception as e:
        return f"<h1>Provider Dashboard</h1><p>Template error: {str(e)}</p><p><a href='/provider/login'>← Back to Login</a></p>"

@app.route("/provider/logout")
def provider_logout():
    """Logout provider"""
    session.clear()
    return redirect("/provider/login")

# ─────────────────────────────────────────────
# BOOKING API
# ─────────────────────────────────────────────
@app.route("/api/book-provider", methods=["POST"])
def api_book_provider():
    """Book a specific provider directly"""
    try:
        data = request.get_json(silent=True) or {}
        
        # Generate booking ID
        booking_id = "NS-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Create order with provider information
        order = {
            "booking_id": booking_id,
            "name": data.get("name"),
            "phone": data.get("phone"),
            "address": data.get("address"),
            "service": data.get("service"),
            "service_key": data.get("service_key"),
            "provider_id": data.get("provider_id"),
            "provider_name": data.get("provider_name"),
            "preferred_date": data.get("date"),
            "preferred_time": data.get("time"),
            "notes": data.get("notes", ""),
            "status": "confirmed",
            "payment": "pending",
            "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "booking_type": "direct_provider"
        }
        
        # Validate required fields
        required_fields = ["name", "phone", "address", "service", "provider_id", "provider_name"]
        for field in required_fields:
            if not order.get(field):
                return jsonify(success=False, message=f"Missing required field: {field}"), 400
        
        # For now, just return success (you can add file storage later)
        return jsonify(
            success=True, 
            booking_id=booking_id,
            message="Booking confirmed successfully!",
            order=order
        )
        
    except Exception as e:
        return jsonify(success=False, message=f"Booking failed: {str(e)}"), 500

@app.route("/api/book", methods=["POST"])
def api_book():
    # Check if user is logged in
    if not session.get("user_id"):
        return jsonify(success=False, message="Please log in to book services"), 401
    
    data = request.get_json(silent=True) or {}
    booking_id = "NS-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    order = {
        "booking_id": booking_id,
        "name": data.get("name"),
        "email": session.get("user_email", data.get("email", "")),
        "phone": data.get("phone"),
        "address": data.get("address"),
        "service": data.get("service"),
        "status": "pending",
        "payment": "unpaid",
        "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": session.get("user_id")
    }
    
    # For now, just return success
    return jsonify(success=True, booking_id=booking_id)

@app.route("/api/locations")
def api_locations():
    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
            
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT location FROM service_providers ORDER BY location")
            locations = [row[0] for row in cur.fetchall()]
        
        conn.close()
        return jsonify(success=True, locations=locations)
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/force-populate", methods=["POST", "GET"])
def force_populate_database():
    """Force populate database (clears existing data)"""
    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
        
        with conn.cursor() as cur:
            # Clear existing providers
            cur.execute("DELETE FROM service_providers")
            print("🗑️ Cleared existing providers")
            
            # Add comprehensive providers with GPS coordinates
            providers = [
                # Home Cleaning Providers
                ("Aarav Sharma", "Home Cleaning", "cleaning", "Butwal", "Rupandehi", 27.7012, 83.4523, 4.8, 5, 312, 0.02, 1.5, True, 148, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face", "9801000001"),
                ("Sita Lama", "Home Cleaning", "cleaning", "Tilottama", "Rupandehi", 27.7189, 83.4287, 4.9, 6, 420, 0.01, 1.0, True, 210, "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face", "9801000002"),
                ("Maya Gurung", "Home Cleaning", "cleaning", "Bhairahawa", "Rupandehi", 27.5095, 83.4534, 4.3, 2, 67, 0.08, 4.0, False, 34, "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face", "9801000003"),
                
                # Plumbing Providers
                ("Arjun Basnet", "Plumbing", "plumber", "Butwal", "Rupandehi", 27.6987, 83.4478, 4.7, 4, 198, 0.03, 2.0, True, 95, "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face", "9801000004"),
                ("Hari Sharma", "Plumbing", "plumber", "Tilottama", "Rupandehi", 27.7234, 83.4312, 4.5, 3, 156, 0.05, 2.5, True, 78, "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face", "9801000005"),
                ("Raju Maharjan", "Plumbing", "plumber", "Chitwan", "Chitwan", 27.5278, 84.3567, 4.6, 6, 234, 0.02, 2.0, True, 117, "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face", "9801000006"),
                
                # Electrician Providers
                ("Deepa Rana", "Electric Repair", "electrician", "Bhairahawa", "Rupandehi", 27.5067, 83.4501, 5.0, 4, 175, 0.00, 2.5, True, 88, "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&h=150&fit=crop&crop=face", "9801000007"),
                ("Ram Bahadur", "Electric Repair", "electrician", "Butwal", "Rupandehi", 27.7023, 83.4489, 4.8, 5, 312, 0.02, 1.5, True, 148, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face", "9801000008"),
                ("Bikash Tamang", "Electric Repair", "electrician", "Chitwan", "Chitwan", 27.5312, 84.3523, 4.4, 3, 123, 0.05, 3.0, False, 61, "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face", "9801000009"),
                
                # AC Service Providers
                ("Sunita Oli", "AC Service", "ac", "Tilottama", "Rupandehi", 27.7156, 83.4298, 4.7, 3, 134, 0.04, 2.0, True, 67, "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face", "9801000010"),
                ("Binod KC", "AC Service", "ac", "Butwal", "Rupandehi", 27.6998, 83.4512, 4.5, 4, 220, 0.03, 2.0, True, 110, "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face", "9801000011"),
                ("Nabin Karki", "AC Service", "ac", "Bhairahawa", "Rupandehi", 27.5089, 83.4487, 4.6, 5, 178, 0.03, 2.0, True, 89, "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face", "9801000012"),
                
                # Hair Cutting Providers
                ("Binod Joshi", "Hair Cutting", "haircutting", "Butwal", "Rupandehi", 27.7034, 83.4456, 4.2, 2, 89, 0.07, 3.0, False, 42, "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face", "9801000013"),
                ("Ramesh Tamang", "Hair Cutting", "haircutting", "Tilottama", "Rupandehi", 27.7201, 83.4334, 4.5, 4, 145, 0.04, 2.5, True, 73, "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face", "9801000014"),
                ("Sabita Chhetri", "Hair Cutting", "haircutting", "Chitwan", "Chitwan", 27.5289, 84.3578, 4.8, 7, 289, 0.02, 1.5, True, 145, "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=150&h=150&fit=crop&crop=face", "9801000015"),
                
                # Makeup Artist Providers
                ("Karuna Rai", "Makeup Artist", "makeup", "Butwal", "Rupandehi", 27.6976, 83.4534, 4.9, 6, 420, 0.01, 1.0, True, 210, "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=150&h=150&fit=crop&crop=face", "9801000016"),
                ("Gita KC", "Makeup Artist", "makeup", "Tilottama", "Rupandehi", 27.7178, 83.4267, 5.0, 4, 175, 0.00, 2.5, True, 88, "https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?w=150&h=150&fit=crop&crop=face", "9801000017"),
                ("Priya Shrestha", "Makeup Artist", "makeup", "Bhairahawa", "Rupandehi", 27.5078, 83.4523, 4.8, 5, 260, 0.02, 2.0, True, 130, "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=150&h=150&fit=crop&crop=face", "9801000018"),
                
                # Photographer Providers
                ("Nisha Koirala", "Photographer", "photographer", "Chitwan", "Chitwan", 27.5267, 84.3589, 4.9, 8, 310, 0.01, 3.0, True, 155, "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=150&h=150&fit=crop&crop=face", "9801000019"),
                ("Anil Shakya", "Photographer", "photographer", "Butwal", "Rupandehi", 27.7045, 83.4467, 4.7, 6, 234, 0.02, 2.5, True, 117, "https://images.unsplash.com/photo-1566492031773-4f4e44671d66?w=150&h=150&fit=crop&crop=face", "9801000020"),
                ("Puja Manandhar", "Photographer", "photographer", "Tilottama", "Rupandehi", 27.7167, 83.4289, 4.4, 3, 123, 0.04, 3.0, True, 62, "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?w=150&h=150&fit=crop&crop=face", "9801000021"),
                
                # Gardener Providers
                ("Mamata Neupane", "Gardener", "gardener", "Bhairahawa", "Rupandehi", 27.5101, 83.4456, 4.3, 6, 145, 0.06, 4.0, False, 72, "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=150&h=150&fit=crop&crop=face", "9801000022"),
                ("Rajesh Pandey", "Gardener", "gardener", "Butwal", "Rupandehi", 27.6989, 83.4501, 4.4, 5, 123, 0.05, 3.0, True, 62, "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150&h=150&fit=crop&crop=face", "9801000023"),
                ("Dilip Tharu", "Gardener", "gardener", "Chitwan", "Chitwan", 27.5301, 84.3534, 4.2, 4, 98, 0.07, 3.5, False, 49, "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face", "9801000024"),
                
                # Maid Service Providers
                ("Anita Thapa", "Maid Service", "maid", "Tilottama", "Rupandehi", 27.7145, 83.4323, 4.6, 7, 380, 0.02, 1.5, True, 190, "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=150&h=150&fit=crop&crop=face", "9801000025"),
                ("Devi Pun", "Maid Service", "maid", "Butwal", "Rupandehi", 27.7056, 83.4478, 4.2, 3, 89, 0.07, 3.5, False, 45, "https://images.unsplash.com/photo-1520813792240-56fc4a3765a7?w=150&h=150&fit=crop&crop=face", "9801000026"),
                ("Bishnu Ghale", "Maid Service", "maid", "Bhairahawa", "Rupandehi", 27.5112, 83.4467, 4.8, 9, 567, 0.01, 1.0, True, 284, "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=150&h=150&fit=crop&crop=face", "9801000027"),
                
                # Technician Service Providers
                ("Deepak Gurung", "Technician Service", "technician", "Chitwan", "Chitwan", 27.5323, 84.3545, 4.4, 3, 112, 0.05, 3.5, False, 55, "https://images.unsplash.com/photo-1499952127939-9bbf5af6c51c?w=150&h=150&fit=crop&crop=face", "9801000028"),
                ("Gopal Adhikari", "Technician Service", "technician", "Butwal", "Rupandehi", 27.7067, 83.4489, 4.7, 6, 234, 0.02, 1.5, True, 117, "https://images.unsplash.com/photo-1496345875659-11f7dd282d1d?w=150&h=150&fit=crop&crop=face", "9801000029"),
                ("Mina Oli", "Technician Service", "technician", "Tilottama", "Rupandehi", 27.7189, 83.4301, 4.1, 2, 56, 0.08, 4.0, False, 28, "https://images.unsplash.com/photo-1521119989659-a83eee488004?w=150&h=150&fit=crop&crop=face", "9801000030")
            ]
            
            for provider in providers:
                cur.execute("""
                    INSERT INTO service_providers 
                    (name, service, service_key, location, district, latitude, longitude, rating, experience, 
                     completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                     review_count, image, phone, availability)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, provider + ('["Mon","Tue","Wed","Thu","Fri","Sat"]',))
            
            # Get final count
            cur.execute("SELECT COUNT(*) FROM service_providers")
            final_count = cur.fetchone()[0]
            print(f"✅ Added {final_count} providers")
        
        conn.close()
        return jsonify(success=True, message=f"Force populated database with {final_count} providers!")
        
    except Exception as e:
        print(f"❌ Force populate error: {e}")
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/populate-db", methods=["POST", "GET"])
def populate_db_endpoint():
    """Manually populate database with providers"""
    try:
        result = populate_database_internal()
        return jsonify(success=True, message=result)
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}")

@app.route("/api/fix-nearby-providers", methods=["POST"])
def fix_nearby_providers():
    """Add GPS coordinates to all providers so they show up in nearby search"""
    try:
        conn = get_db()
        if not conn:
            return jsonify(success=False, message="Database not available")
            
        with conn.cursor() as cur:
            # Location coordinates for your areas
            location_coords = {
                'Butwal': {'lat': 27.7000, 'lng': 83.4500},
                'Tilottama': {'lat': 27.7200, 'lng': 83.4300}, 
                'Bhairahawa': {'lat': 27.5081, 'lng': 83.4519},
                'Chitwan': {'lat': 27.5291, 'lng': 84.3542},
                'Siddharthanagar': {'lat': 27.5200, 'lng': 83.4600},
                'Devdaha': {'lat': 27.6800, 'lng': 83.4200}
            }
            
            # Get all providers without GPS coordinates
            cur.execute("""
                SELECT id, name, location 
                FROM service_providers 
                WHERE latitude IS NULL OR longitude IS NULL
            """)
            providers_without_gps = cur.fetchall()
            
            updated_count = 0
            
            for provider in providers_without_gps:
                location = provider[2]
                if location in location_coords:
                    base_coords = location_coords[location]
                    
                    # Add small random offset (within 2km) to spread providers around the area
                    lat_offset = random.uniform(-0.018, 0.018)  # ~2km in degrees
                    lng_offset = random.uniform(-0.018, 0.018)
                    
                    final_lat = base_coords['lat'] + lat_offset
                    final_lng = base_coords['lng'] + lng_offset
                    
                    # Update provider with GPS coordinates
                    cur.execute("""
                        UPDATE service_providers 
                        SET latitude = %s, longitude = %s 
                        WHERE id = %s
                    """, (final_lat, final_lng, provider[0]))
                    
                    updated_count += 1
            
            conn.close()
            return jsonify(
                success=True, 
                message=f"Added GPS coordinates to {updated_count} providers",
                updated_count=updated_count
            )
        
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}"), 500

def initialize_app():
    """Initialize the application for production"""
    print("🚀 NepSewa - Initializing full production deployment")
    
    # Setup database
    db_configured = setup_database_config()
    
    if db_configured:
        db_initialized = init_db()
        print(f"✅ Database initialization: {'success' if db_initialized else 'failed'}")
        
        # Auto-populate database if empty
        try:
            conn = get_db()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM service_providers")
                    count = cur.fetchone()[0]
                    print(f"📊 Current provider count: {count}")
                    if count == 0:
                        print("📊 Database is empty, auto-populating with sample data...")
                        # Call the populate function directly
                        populate_result = populate_database_internal()
                        print(f"✅ Auto-population: {populate_result}")
                    else:
                        print(f"✅ Database already has {count} providers")
                conn.close()
        except Exception as e:
            print(f"⚠️ Auto-population warning: {e}")
            # Force populate on error
            try:
                populate_result = populate_database_internal()
                print(f"🔄 Force population result: {populate_result}")
            except Exception as e2:
                print(f"❌ Force population failed: {e2}")
    
    # Set Flask configuration for production
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    
    print("✅ Full NepSewa application initialized successfully")
    return app

def populate_database_internal():
    """Internal function to populate database"""
    try:
        conn = get_db()
        if not conn:
            return "Database not available"
        
        with conn.cursor() as cur:
            # Add comprehensive providers with GPS coordinates
            providers = [
                # Home Cleaning Providers
                ("Aarav Sharma", "Home Cleaning", "cleaning", "Butwal", "Rupandehi", 27.7012, 83.4523, 4.8, 5, 312, 0.02, 1.5, True, 148, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face", "9801000001"),
                ("Sita Lama", "Home Cleaning", "cleaning", "Tilottama", "Rupandehi", 27.7189, 83.4287, 4.9, 6, 420, 0.01, 1.0, True, 210, "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face", "9801000002"),
                ("Maya Gurung", "Home Cleaning", "cleaning", "Bhairahawa", "Rupandehi", 27.5095, 83.4534, 4.3, 2, 67, 0.08, 4.0, False, 34, "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face", "9801000003"),
                
                # Plumbing Providers
                ("Arjun Basnet", "Plumbing", "plumber", "Butwal", "Rupandehi", 27.6987, 83.4478, 4.7, 4, 198, 0.03, 2.0, True, 95, "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face", "9801000004"),
                ("Hari Sharma", "Plumbing", "plumber", "Tilottama", "Rupandehi", 27.7234, 83.4312, 4.5, 3, 156, 0.05, 2.5, True, 78, "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face", "9801000005"),
                ("Raju Maharjan", "Plumbing", "plumber", "Chitwan", "Chitwan", 27.5278, 84.3567, 4.6, 6, 234, 0.02, 2.0, True, 117, "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face", "9801000006"),
                
                # Electrician Providers
                ("Deepa Rana", "Electric Repair", "electrician", "Bhairahawa", "Rupandehi", 27.5067, 83.4501, 5.0, 4, 175, 0.00, 2.5, True, 88, "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&h=150&fit=crop&crop=face", "9801000007"),
                ("Ram Bahadur", "Electric Repair", "electrician", "Butwal", "Rupandehi", 27.7023, 83.4489, 4.8, 5, 312, 0.02, 1.5, True, 148, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face", "9801000008"),
                ("Bikash Tamang", "Electric Repair", "electrician", "Chitwan", "Chitwan", 27.5312, 84.3523, 4.4, 3, 123, 0.05, 3.0, False, 61, "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face", "9801000009"),
                
                # AC Service Providers
                ("Sunita Oli", "AC Service", "ac", "Tilottama", "Rupandehi", 27.7156, 83.4298, 4.7, 3, 134, 0.04, 2.0, True, 67, "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face", "9801000010"),
                ("Binod KC", "AC Service", "ac", "Butwal", "Rupandehi", 27.6998, 83.4512, 4.5, 4, 220, 0.03, 2.0, True, 110, "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face", "9801000011"),
                ("Nabin Karki", "AC Service", "ac", "Bhairahawa", "Rupandehi", 27.5089, 83.4487, 4.6, 5, 178, 0.03, 2.0, True, 89, "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face", "9801000012"),
                
                # Hair Cutting Providers
                ("Binod Joshi", "Hair Cutting", "haircutting", "Butwal", "Rupandehi", 27.7034, 83.4456, 4.2, 2, 89, 0.07, 3.0, False, 42, "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face", "9801000013"),
                ("Ramesh Tamang", "Hair Cutting", "haircutting", "Tilottama", "Rupandehi", 27.7201, 83.4334, 4.5, 4, 145, 0.04, 2.5, True, 73, "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face", "9801000014"),
                ("Sabita Chhetri", "Hair Cutting", "haircutting", "Chitwan", "Chitwan", 27.5289, 84.3578, 4.8, 7, 289, 0.02, 1.5, True, 145, "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=150&h=150&fit=crop&crop=face", "9801000015"),
                
                # Makeup Artist Providers
                ("Karuna Rai", "Makeup Artist", "makeup", "Butwal", "Rupandehi", 27.6976, 83.4534, 4.9, 6, 420, 0.01, 1.0, True, 210, "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=150&h=150&fit=crop&crop=face", "9801000016"),
                ("Gita KC", "Makeup Artist", "makeup", "Tilottama", "Rupandehi", 27.7178, 83.4267, 5.0, 4, 175, 0.00, 2.5, True, 88, "https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?w=150&h=150&fit=crop&crop=face", "9801000017"),
                ("Priya Shrestha", "Makeup Artist", "makeup", "Bhairahawa", "Rupandehi", 27.5078, 83.4523, 4.8, 5, 260, 0.02, 2.0, True, 130, "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=150&h=150&fit=crop&crop=face", "9801000018"),
                
                # Photographer Providers
                ("Nisha Koirala", "Photographer", "photographer", "Chitwan", "Chitwan", 27.5267, 84.3589, 4.9, 8, 310, 0.01, 3.0, True, 155, "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=150&h=150&fit=crop&crop=face", "9801000019"),
                ("Anil Shakya", "Photographer", "photographer", "Butwal", "Rupandehi", 27.7045, 83.4467, 4.7, 6, 234, 0.02, 2.5, True, 117, "https://images.unsplash.com/photo-1566492031773-4f4e44671d66?w=150&h=150&fit=crop&crop=face", "9801000020"),
                ("Puja Manandhar", "Photographer", "photographer", "Tilottama", "Rupandehi", 27.7167, 83.4289, 4.4, 3, 123, 0.04, 3.0, True, 62, "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?w=150&h=150&fit=crop&crop=face", "9801000021"),
                
                # Gardener Providers
                ("Mamata Neupane", "Gardener", "gardener", "Bhairahawa", "Rupandehi", 27.5101, 83.4456, 4.3, 6, 145, 0.06, 4.0, False, 72, "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=150&h=150&fit=crop&crop=face", "9801000022"),
                ("Rajesh Pandey", "Gardener", "gardener", "Butwal", "Rupandehi", 27.6989, 83.4501, 4.4, 5, 123, 0.05, 3.0, True, 62, "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150&h=150&fit=crop&crop=face", "9801000023"),
                ("Dilip Tharu", "Gardener", "gardener", "Chitwan", "Chitwan", 27.5301, 84.3534, 4.2, 4, 98, 0.07, 3.5, False, 49, "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face", "9801000024"),
                
                # Maid Service Providers
                ("Anita Thapa", "Maid Service", "maid", "Tilottama", "Rupandehi", 27.7145, 83.4323, 4.6, 7, 380, 0.02, 1.5, True, 190, "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=150&h=150&fit=crop&crop=face", "9801000025"),
                ("Devi Pun", "Maid Service", "maid", "Butwal", "Rupandehi", 27.7056, 83.4478, 4.2, 3, 89, 0.07, 3.5, False, 45, "https://images.unsplash.com/photo-1520813792240-56fc4a3765a7?w=150&h=150&fit=crop&crop=face", "9801000026"),
                ("Bishnu Ghale", "Maid Service", "maid", "Bhairahawa", "Rupandehi", 27.5112, 83.4467, 4.8, 9, 567, 0.01, 1.0, True, 284, "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=150&h=150&fit=crop&crop=face", "9801000027"),
                
                # Technician Service Providers
                ("Deepak Gurung", "Technician Service", "technician", "Chitwan", "Chitwan", 27.5323, 84.3545, 4.4, 3, 112, 0.05, 3.5, False, 55, "https://images.unsplash.com/photo-1499952127939-9bbf5af6c51c?w=150&h=150&fit=crop&crop=face", "9801000028"),
                ("Gopal Adhikari", "Technician Service", "technician", "Butwal", "Rupandehi", 27.7067, 83.4489, 4.7, 6, 234, 0.02, 1.5, True, 117, "https://images.unsplash.com/photo-1496345875659-11f7dd282d1d?w=150&h=150&fit=crop&crop=face", "9801000029"),
                ("Mina Oli", "Technician Service", "technician", "Tilottama", "Rupandehi", 27.7189, 83.4301, 4.1, 2, 56, 0.08, 4.0, False, 28, "https://images.unsplash.com/photo-1521119989659-a83eee488004?w=150&h=150&fit=crop&crop=face", "9801000030")
            ]
            
            for provider in providers:
                cur.execute("""
                    INSERT INTO service_providers 
                    (name, service, service_key, location, district, latitude, longitude, rating, experience, 
                     completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                     review_count, image, phone, availability)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, provider + ('["Mon","Tue","Wed","Thu","Fri","Sat"]',))
            
            # Get final count
            cur.execute("SELECT COUNT(*) FROM service_providers")
            final_count = cur.fetchone()[0]
        
        conn.close()
        return f"Added {final_count} providers successfully"
        
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize the app
application = initialize_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8001))
    print(f"🌐 Starting full NepSewa server on port {port}")
    application.run(host='0.0.0.0', port=port, debug=False)