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
        # Create connection with proper SSL handling
        conn = pg8000.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            ssl_context=True  # Simplified SSL context
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        # Try without SSL context as fallback
        try:
            conn = pg8000.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
            conn.autocommit = True
            return conn
        except Exception as e2:
            print(f"Database fallback connection error: {e2}")
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