from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json, os, random, string, requests, hmac, hashlib, base64, uuid
from datetime import datetime
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "nepsewa_secret_key_2026"

# ─────────────────────────────────────────────
# FILE UPLOAD CONFIG
# ─────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'providers')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_provider_image(file):
    """Securely save provider image and return the file path"""
    if not file or not allowed_file(file.filename):
        return None
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    
    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    
    # Return relative path for database storage
    return f"/static/uploads/providers/{unique_filename}"

# ─────────────────────────────────────────────
# DB — reconnect-safe helper
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# DB — reconnect-safe helper
# ─────────────────────────────────────────────
DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="nepsewa123",
    database="nepsewa",
    autocommit=True,
    cursorclass=pymysql.cursors.DictCursor
)

def get_db():
    """Get a fresh database connection for each request"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        print("Make sure MySQL is running and credentials are correct")
        raise e

# ─────────────────────────────────────────────
# DB INIT — create table if missing
# ─────────────────────────────────────────────
def init_db():
    conn = get_db()
    with conn.cursor() as cur:
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         INT AUTO_INCREMENT PRIMARY KEY,
                name       VARCHAR(120)  NOT NULL,
                email      VARCHAR(180)  NOT NULL UNIQUE,
                password   VARCHAR(256)  NOT NULL,
                created_at DATETIME      DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Service providers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS service_providers (
                id                  INT AUTO_INCREMENT PRIMARY KEY,
                name                VARCHAR(120) NOT NULL,
                service             VARCHAR(100) NOT NULL,
                service_key         VARCHAR(50)  NOT NULL,
                location            VARCHAR(100) NOT NULL,
                district            VARCHAR(100) NOT NULL,
                rating              DECIMAL(3,2) DEFAULT 0.0,
                experience          INT          DEFAULT 0,
                completed_jobs      INT          DEFAULT 0,
                cancellation_rate   DECIMAL(4,3) DEFAULT 0.0,
                response_time_hours DECIMAL(4,1) DEFAULT 24.0,
                is_verified         BOOLEAN      DEFAULT FALSE,
                review_count        INT          DEFAULT 0,
                image               TEXT,
                phone               VARCHAR(15),
                availability        JSON,
                email               VARCHAR(180) UNIQUE,
                password            VARCHAR(256),
                bio                 TEXT,
                created_at          DATETIME     DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_service_key (service_key),
                INDEX idx_location (location),
                INDEX idx_rating (rating),
                INDEX idx_email (email)
            )
        """)
    conn.commit()
    
    # Insert sample data if table is empty
    insert_sample_providers()

# ─────────────────────────────────────────────
# ESEWA CONFIG
# ─────────────────────────────────────────────
ESEWA_MERCHANT_CODE = "EPAYTEST"
ESEWA_SECRET_KEY    = "8gBm/:&EnhH.1/q"
ESEWA_BASE_URL      = "https://rc-epay.esewa.com.np"

SERVICE_PRICES = {
    "maid": 500, "technician": 300, "plumber": 500,
    "electrician": 500, "haircutting": 200, "gardener": 1000,
    "makeup": 500, "photographer": 500, "cleaning": 500, "ac": 500,
}

# ─────────────────────────────────────────────
# ORDERS (JSON file)
# ─────────────────────────────────────────────
ORDERS_FILE = os.path.join(os.path.dirname(__file__), "orders.json")

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE) as f:
        return json.load(f)

def save_order(order):
    orders = load_orders()
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def update_order_field(booking_id, **fields):
    orders = load_orders()
    for o in orders:
        if o["booking_id"] == booking_id:
            o.update(fields)
            break
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def get_order(booking_id):
    return next((o for o in load_orders() if o["booking_id"] == booking_id), None)

# ─────────────────────────────────────────────
# SAMPLE PROVIDERS DATA
# ─────────────────────────────────────────────
def insert_sample_providers():
    conn = get_db()
    with conn.cursor() as cur:
        # Check if providers already exist
        cur.execute("SELECT COUNT(*) as count FROM service_providers")
        result = cur.fetchone()
        if result["count"] > 0:
            return  # Data already exists
        
        # Sample providers data
        providers = [
            {
                "name": "Ram Bahadur", "service": "Electric Repair", "service_key": "electrician",
                "location": "Kathmandu", "district": "Kathmandu", "rating": 4.8, "experience": 5,
                "completed_jobs": 312, "cancellation_rate": 0.02, "response_time_hours": 1.5,
                "is_verified": True, "review_count": 148, "phone": "9801000001",
                "image": "https://randomuser.me/api/portraits/men/32.jpg",
                "availability": '["Mon","Tue","Wed","Thu","Fri","Sat"]'
            },
            {
                "name": "Sita Lama", "service": "Home Cleaning", "service_key": "cleaning",
                "location": "Lalitpur", "district": "Lalitpur", "rating": 4.9, "experience": 6,
                "completed_jobs": 420, "cancellation_rate": 0.01, "response_time_hours": 1.0,
                "is_verified": True, "review_count": 210, "phone": "9801000002",
                "image": "https://randomuser.me/api/portraits/women/44.jpg",
                "availability": '["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'
            },
            {
                "name": "Hari Sharma", "service": "Plumbing", "service_key": "plumber",
                "location": "Kathmandu", "district": "Kathmandu", "rating": 4.7, "experience": 4,
                "completed_jobs": 198, "cancellation_rate": 0.03, "response_time_hours": 2.0,
                "is_verified": True, "review_count": 95, "phone": "9801000003",
                "image": "https://randomuser.me/api/portraits/men/76.jpg",
                "availability": '["Mon","Tue","Wed","Thu","Fri"]'
            },
            {
                "name": "Gita KC", "service": "Spa & Massage", "service_key": "makeup",
                "location": "Bhaktapur", "district": "Bhaktapur", "rating": 5.0, "experience": 4,
                "completed_jobs": 175, "cancellation_rate": 0.00, "response_time_hours": 2.5,
                "is_verified": True, "review_count": 88, "phone": "9801000004",
                "image": "https://randomuser.me/api/portraits/women/65.jpg",
                "availability": '["Tue","Wed","Thu","Fri","Sat","Sun"]'
            },
            {
                "name": "Ramesh Tamang", "service": "Hair Cutting", "service_key": "haircutting",
                "location": "Kathmandu", "district": "Kathmandu", "rating": 4.2, "experience": 2,
                "completed_jobs": 89, "cancellation_rate": 0.07, "response_time_hours": 3.0,
                "is_verified": False, "review_count": 42, "phone": "9801000005",
                "image": "https://randomuser.me/api/portraits/men/55.jpg",
                "availability": '["Mon","Wed","Fri","Sat","Sun"]'
            },
            {
                "name": "Suman Rai", "service": "Home Cleaning", "service_key": "cleaning",
                "location": "Lalitpur", "district": "Lalitpur", "rating": 4.7, "experience": 3,
                "completed_jobs": 134, "cancellation_rate": 0.04, "response_time_hours": 2.0,
                "is_verified": True, "review_count": 67, "phone": "9801000006",
                "image": "https://randomuser.me/api/portraits/men/66.jpg",
                "availability": '["Mon","Tue","Thu","Fri","Sat"]'
            },
            {
                "name": "Binod KC", "service": "AC Service", "service_key": "ac",
                "location": "Kathmandu", "district": "Kathmandu", "rating": 4.5, "experience": 4,
                "completed_jobs": 220, "cancellation_rate": 0.03, "response_time_hours": 2.0,
                "is_verified": True, "review_count": 110, "phone": "9801000007",
                "image": "https://randomuser.me/api/portraits/men/88.jpg",
                "availability": '["Mon","Tue","Wed","Thu","Fri","Sat"]'
            },
            {
                "name": "Anita Thapa", "service": "Maid Service", "service_key": "maid",
                "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.6, "experience": 7,
                "completed_jobs": 380, "cancellation_rate": 0.02, "response_time_hours": 1.5,
                "is_verified": True, "review_count": 190, "phone": "9801000008",
                "image": "https://randomuser.me/api/portraits/women/33.jpg",
                "availability": '["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'
            },
            {
                "name": "Deepak Gurung", "service": "Plumbing", "service_key": "plumber",
                "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.4, "experience": 3,
                "completed_jobs": 112, "cancellation_rate": 0.05, "response_time_hours": 3.5,
                "is_verified": False, "review_count": 55, "phone": "9801000009",
                "image": "https://randomuser.me/api/portraits/men/41.jpg",
                "availability": '["Tue","Wed","Fri","Sat"]'
            },
            {
                "name": "Priya Shrestha", "service": "Makeup Artist", "service_key": "makeup",
                "location": "Kathmandu", "district": "Kathmandu", "rating": 4.8, "experience": 5,
                "completed_jobs": 260, "cancellation_rate": 0.02, "response_time_hours": 2.0,
                "is_verified": True, "review_count": 130, "phone": "9801000010",
                "image": "https://randomuser.me/api/portraits/women/58.jpg",
                "availability": '["Mon","Wed","Thu","Fri","Sat","Sun"]'
            },
            {
                "name": "Rajesh Pandey", "service": "Gardener", "service_key": "gardener",
                "location": "Lalitpur", "district": "Lalitpur", "rating": 4.3, "experience": 6,
                "completed_jobs": 145, "cancellation_rate": 0.06, "response_time_hours": 4.0,
                "is_verified": False, "review_count": 72, "phone": "9801000011",
                "image": "https://randomuser.me/api/portraits/men/62.jpg",
                "availability": '["Mon","Tue","Thu","Sat","Sun"]'
            },
            {
                "name": "Nisha Maharjan", "service": "Photographer", "service_key": "photographer",
                "location": "Kathmandu", "district": "Kathmandu", "rating": 4.9, "experience": 8,
                "completed_jobs": 310, "cancellation_rate": 0.01, "response_time_hours": 3.0,
                "is_verified": True, "review_count": 155, "phone": "9801000012",
                "image": "https://randomuser.me/api/portraits/women/22.jpg",
                "availability": '["Fri","Sat","Sun"]'
            }
        ]
        
        # Insert providers
        for provider in providers:
            cur.execute("""
                INSERT INTO service_providers 
                (name, service, service_key, location, district, rating, experience, 
                 completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                 review_count, image, phone, availability)
                VALUES (%(name)s, %(service)s, %(service_key)s, %(location)s, %(district)s, 
                        %(rating)s, %(experience)s, %(completed_jobs)s, %(cancellation_rate)s, 
                        %(response_time_hours)s, %(is_verified)s, %(review_count)s, 
                        %(image)s, %(phone)s, %(availability)s)
            """, provider)
    
    conn.commit()
    print("Sample providers inserted successfully!")

# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────
@app.route("/")
def home():
    try:
        return render_template("nepsewa.html")
    except Exception as e:
        print(f"Error in home route: {e}")
        return f"Error loading home page: {str(e)}", 500

@app.route("/services")
def services():
    try:
        return render_template("services.html")
    except Exception as e:
        print(f"Error in services route: {e}")
        return f"Error loading services page: {str(e)}", 500

@app.route("/register-provider")
def register_provider_page():
    """Provider registration page (original form)"""
    return render_template("register_provider.html")

@app.route("/health")
def health_check():
    try:
        # Test database connection
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "message": "NepSewa API is running"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route("/admin/dashboard")
def admin_dashboard():
    """Dashboard overview page"""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login_page"))
    return render_template("admin_dashboard_home.html")

@app.route("/admin/approvals")
def admin_approvals():
    """Worker approvals page"""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login_page"))
    return render_template("admin_approvals.html")

@app.route("/admin/workers")
def admin_workers():
    """Workers management page"""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login_page"))
    return render_template("admin_dashboard_clean.html")

@app.route("/admin/payments")
def admin_payments():
    """Payments and finance page"""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login_page"))
    return render_template("admin_payments.html")
def admin_workers():
    """Workers management page"""
    return render_template("admin_dashboard_clean.html")

@app.route("/admin/manage-providers")
def manage_providers_page():
    """Admin page to manage all providers"""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login_page"))
    return render_template("manage_providers.html")
@app.route("/login")
def login_page():
    if session.get("user_id"):
        # User is already logged in, check for redirect
        redirect_url = request.args.get("redirect", "/profile")
        return redirect(redirect_url)
    return render_template("login.html")

@app.route("/profile")
def profile_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("profile.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ─────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────
@app.route("/admin")
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/admin/login", methods=["POST"])
def admin_login():
    if request.form.get("password") == "admin123":
        session["is_admin"] = True
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html", error="Wrong password")

@app.route("/orders")
def orders_page():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login_page"))
    return render_template("orders.html", orders=list(reversed(load_orders())))

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login_page"))

# ─────────────────────────────────────────────
# PROVIDER PORTAL
# ─────────────────────────────────────────────
@app.route("/provider/login")
def provider_login_page():
    if session.get("provider_id"):
        return redirect(url_for("provider_dashboard"))
    return render_template("provider_login.html")

@app.route("/provider/register")
def provider_register_page():
    return render_template("provider_register.html")

@app.route("/provider/dashboard")
def provider_dashboard():
    if not session.get("provider_id"):
        return redirect(url_for("provider_login_page"))
    return render_template("provider_dashboard.html")

@app.route("/provider/profile")
def provider_profile_page():
    if not session.get("provider_id"):
        return redirect(url_for("provider_login_page"))
    return render_template("provider_profile.html")

@app.route("/provider/logout")
def provider_logout():
    session.pop("provider_id", None)
    session.pop("provider_name", None)
    session.pop("provider_email", None)
    return redirect(url_for("provider_login_page"))

# ─────────────────────────────────────────────
# AUTH API
# ─────────────────────────────────────────────
@app.route("/api/signup", methods=["POST"])
def signup():
    data     = request.get_json(silent=True) or {}
    name     = (data.get("name")     or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not name or not email or not password:
        return jsonify(success=False, message="All fields are required")
    if len(password) < 6:
        return jsonify(success=False, message="Password must be at least 6 characters")

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            return jsonify(success=False, message="Email already registered")
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, generate_password_hash(password))
        )
    conn.commit()
    return jsonify(success=True, message="Account created successfully")


@app.route("/api/login", methods=["POST"])
def login():
    data     = request.get_json(silent=True) or {}
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify(success=False, message="All fields are required")

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, email, password, created_at FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

    if not user or not check_password_hash(user["password"], password):
        return jsonify(success=False, message="Invalid email or password")

    session["user_id"]    = user["id"]
    session["user_name"]  = user["name"]
    session["user_email"] = user["email"]
    
    # Check for redirect URL
    redirect_url = data.get("redirect_url", "/profile")
    
    return jsonify(success=True, message="Login successful", redirect_url=redirect_url)


# ─────────────────────────────────────────────
# PROVIDER AUTH API
# ─────────────────────────────────────────────
@app.route("/api/provider/register", methods=["POST"])
def provider_register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    phone = (data.get("phone") or "").strip()
    service = data.get("service")
    location = data.get("location")
    experience = int(data.get("experience", 1))
    bio = (data.get("bio") or "").strip()

    if not all([name, email, password, phone, service, location]):
        return jsonify(success=False, message="All required fields must be filled")
    
    if len(password) < 6:
        return jsonify(success=False, message="Password must be at least 6 characters")

    # Map service names to keys
    service_mapping = {
        "Home Cleaning": "cleaning", "Plumbing": "plumber", "Electric Repair": "electrician",
        "AC Service": "ac", "Maid Service": "maid", "Technician Service": "technician",
        "Hair Cutting": "haircutting", "Gardener": "gardener", "Makeup Artist": "makeup",
        "Photographer": "photographer"
    }
    service_key = service_mapping.get(service, "other")

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Check if email already exists
            cur.execute("SELECT id FROM service_providers WHERE email=%s", (email,))
            if cur.fetchone():
                return jsonify(success=False, message="Email already registered")
            
            # Insert new provider
            cur.execute("""
                INSERT INTO service_providers 
                (name, email, password, phone, service, service_key, location, district, 
                 experience, bio, rating, completed_jobs, is_verified, review_count, 
                 cancellation_rate, response_time_hours, availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                name, email, generate_password_hash(password), phone, service, service_key,
                location, location, experience, bio, 4.0, 0, False, 0, 0.05, 2.0,
                '["Mon","Tue","Wed","Thu","Fri","Sat"]'
            ))
        
        conn.commit()
        return jsonify(success=True, message="Registration successful! Please wait for admin approval.")
    except Exception as e:
        return jsonify(success=False, message=f"Registration failed: {str(e)}"), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/provider/login", methods=["POST"])
def provider_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify(success=False, message="All fields are required")

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email, password, service, location, is_verified, image, phone
                FROM service_providers WHERE email=%s
            """, (email,))
            provider = cur.fetchone()

        if not provider:
            return jsonify(success=False, message="Invalid email or password")
        
        if not provider["password"]:
            return jsonify(success=False, message="Please register with a password first")
        
        if not check_password_hash(provider["password"], password):
            return jsonify(success=False, message="Invalid email or password")

        session["provider_id"] = provider["id"]
        session["provider_name"] = provider["name"]
        session["provider_email"] = provider["email"]
        
        return jsonify(success=True, message="Login successful", redirect_url="/provider/dashboard")
    except Exception as e:
        return jsonify(success=False, message=f"Login failed: {str(e)}"), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/provider/me")
def provider_me():
    if not session.get("provider_id"):
        return jsonify(success=False, message="Not logged in"), 401

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email, phone, service, service_key, location, district,
                       rating, experience, completed_jobs, cancellation_rate, response_time_hours,
                       is_verified, review_count, image, bio, availability, created_at
                FROM service_providers WHERE id=%s
            """, (session["provider_id"],))
            provider = cur.fetchone()

        if not provider:
            session.clear()
            return jsonify(success=False, message="Provider not found"), 404

        # Parse availability JSON
        try:
            provider["availability"] = json.loads(provider["availability"]) if provider["availability"] else []
        except:
            provider["availability"] = []

        return jsonify(success=True, provider=provider)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/provider/update", methods=["PUT"])
def provider_update():
    if not session.get("provider_id"):
        return jsonify(success=False, message="Not logged in"), 401

    data = request.get_json(silent=True) or {}
    
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Build update query dynamically based on provided fields
            updates = []
            params = []
            
            if "name" in data:
                updates.append("name = %s")
                params.append(data["name"])
            
            if "phone" in data:
                updates.append("phone = %s")
                params.append(data["phone"])
            
            if "location" in data:
                updates.append("location = %s")
                params.append(data["location"])
                updates.append("district = %s")
                params.append(data["location"])
            
            if "experience" in data:
                updates.append("experience = %s")
                params.append(int(data["experience"]))
            
            if "bio" in data:
                updates.append("bio = %s")
                params.append(data["bio"])
            
            if "availability" in data:
                updates.append("availability = %s")
                params.append(json.dumps(data["availability"]))
            
            if "image" in data:
                updates.append("image = %s")
                params.append(data["image"])
            
            if not updates:
                return jsonify(success=False, message="No fields to update")
            
            params.append(session["provider_id"])
            query = f"UPDATE service_providers SET {', '.join(updates)} WHERE id = %s"
            
            cur.execute(query, params)
        
        conn.commit()
        return jsonify(success=True, message="Profile updated successfully!")
    except Exception as e:
        return jsonify(success=False, message=f"Update failed: {str(e)}"), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/provider/stats")
def provider_stats():
    if not session.get("provider_id"):
        return jsonify(success=False, message="Not logged in"), 401

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT completed_jobs, rating, review_count, is_verified
                FROM service_providers WHERE id=%s
            """, (session["provider_id"],))
            stats = cur.fetchone()

        if not stats:
            return jsonify(success=False, message="Provider not found"), 404

        # Calculate estimated earnings (assuming average Rs. 500 per job)
        estimated_earnings = stats["completed_jobs"] * 500

        return jsonify(success=True, stats={
            "completed_jobs": stats["completed_jobs"],
            "rating": float(stats["rating"]),
            "review_count": stats["review_count"],
            "is_verified": bool(stats["is_verified"]),
            "estimated_earnings": estimated_earnings
        })
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/me")
def api_me():
    if not session.get("user_id"):
        return jsonify(success=False, message="Not logged in"), 401

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, email, created_at FROM users WHERE id=%s",
            (session["user_id"],)
        )
        user = cur.fetchone()

    if not user:
        session.clear()
        return jsonify(success=False, message="User not found"), 404

    # Get user's bookings
    bookings = [o for o in load_orders() if o.get("email") == user["email"] or o.get("user_id") == user["id"]]

    return jsonify(
        success=True,
        user=dict(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            member_since=str(user["created_at"])[:10],
            total_bookings=len(bookings),
            bookings=bookings[-5:],  # Last 5 bookings
            initials="".join(w[0].upper() for w in user["name"].split()[:2])
        )
    )


# ─────────────────────────────────────────────
# BOOKING API
# ─────────────────────────────────────────────
@app.route("/api/book", methods=["POST"])
def api_book():
    # Check if user is logged in
    if not session.get("user_id"):
        return jsonify(success=False, message="Please log in to book services"), 401
    
    data = request.get_json(silent=True) or {}
    booking_id = "NS-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    order = {
        "booking_id": booking_id,
        "name":       data.get("name"),
        "email":      session.get("user_email", data.get("email", "")),
        "phone":      data.get("phone"),
        "address":    data.get("address"),
        "service":    data.get("service"),
        "status":     "pending",
        "payment":    "unpaid",
        "booked_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id":    session.get("user_id")  # Link booking to user
    }
    save_order(order)
    return jsonify(success=True, booking_id=booking_id)


@app.route("/api/orders")
def api_orders():
    """Get all orders for dashboard"""
    try:
        orders = load_orders()
        return jsonify(success=True, orders=orders)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route("/api/orders/update", methods=["POST"])
def api_update_order():
    data = request.get_json(silent=True) or {}
    booking_id = data.get("booking_id")
    
    if not booking_id:
        return jsonify(success=False, message="Booking ID required"), 400
    
    # Update order fields
    update_fields = {}
    if "status" in data:
        update_fields["status"] = data["status"]
    if "payment" in data:
        update_fields["payment"] = data["payment"]
    
    update_order_field(booking_id, **update_fields)
    return jsonify(success=True, message="Order updated successfully")


@app.route("/api/payments/stats")
def api_payment_stats():
    """Get payment statistics for admin dashboard"""
    if not session.get("is_admin"):
        return jsonify(success=False, message="Unauthorized"), 401
    
    try:
        orders = load_orders()
        
        # Service prices for calculation
        service_prices = {
            "maid": 500, "technician": 300, "plumber": 500,
            "electrician": 500, "haircutting": 200, "gardener": 1000,
            "makeup": 500, "photographer": 500, "cleaning": 500, "ac": 500,
            "Maid Service": 500, "Technician Service": 300, "Plumbing": 500,
            "Electric Repair": 500, "Hair Cutting": 200, "Gardener": 1000,
            "Makeup Artist": 500, "Photographer": 500, "Home Cleaning": 500, "AC Service": 500
        }
        
        # Calculate stats
        paid_orders = [o for o in orders if o.get("payment") == "paid"]
        pending_orders = [o for o in orders if o.get("payment") != "paid"]
        
        total_revenue = sum(service_prices.get(order.get("service"), 500) for order in paid_orders)
        avg_order_value = total_revenue / len(paid_orders) if paid_orders else 0
        
        # Payment method breakdown
        payment_methods = {}
        for order in paid_orders:
            # Simulate payment methods
            method = "eSewa" if "esewa" in order.get("booking_id", "").lower() else "Cash"
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        return jsonify(success=True, stats={
            "total_revenue": total_revenue,
            "paid_orders": len(paid_orders),
            "pending_payments": len(pending_orders),
            "avg_order_value": round(avg_order_value),
            "payment_methods": payment_methods,
            "total_orders": len(orders)
        })
        
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route("/api/payments/history")
def api_payment_history():
    """Get detailed payment history"""
    if not session.get("is_admin"):
        return jsonify(success=False, message="Unauthorized"), 401
    
    try:
        orders = load_orders()
        
        # Service prices
        service_prices = {
            "maid": 500, "technician": 300, "plumber": 500,
            "electrician": 500, "haircutting": 200, "gardener": 1000,
            "makeup": 500, "photographer": 500, "cleaning": 500, "ac": 500,
            "Maid Service": 500, "Technician Service": 300, "Plumbing": 500,
            "Electric Repair": 500, "Hair Cutting": 200, "Gardener": 1000,
            "Makeup Artist": 500, "Photographer": 500, "Home Cleaning": 500, "AC Service": 500
        }
        
        # Convert orders to payment records
        payments = []
        for order in orders:
            payment = {
                "id": f"PAY-{order['booking_id'].replace('NS-', '')}",
                "order_id": order["booking_id"],
                "customer": order["name"],
                "service": order["service"],
                "amount": service_prices.get(order["service"], 500),
                "status": order.get("payment", "unpaid"),
                "date": order["booked_at"],
                "phone": order.get("phone", ""),
                "email": order.get("email", ""),
                "method": "eSewa" if order.get("payment") == "paid" else "Pending"
            }
            payments.append(payment)
        
        return jsonify(success=True, payments=payments)
        
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


# ─────────────────────────────────────────────
# PROVIDERS API
# ─────────────────────────────────────────────
@app.route("/api/providers")
def api_providers():
    service_key = request.args.get("service_key", "")
    location = request.args.get("location", "")
    day_name = request.args.get("day_name", "")
    min_rating = float(request.args.get("min_rating", 0))
    sort_by = request.args.get("sort", "score")
    
    conn = get_db()
    with conn.cursor() as cur:
        # Build dynamic query
        query = "SELECT * FROM service_providers WHERE 1=1"
        params = []
        
        if service_key:
            query += " AND service_key = %s"
            params.append(service_key)
        
        if location:
            query += " AND location = %s"
            params.append(location)
            
        if min_rating > 0:
            query += " AND rating >= %s"
            params.append(min_rating)
        
        cur.execute(query, params)
        providers = cur.fetchall()
    
    # Filter by day availability if specified
    if day_name:
        filtered_providers = []
        for p in providers:
            try:
                availability = json.loads(p["availability"]) if p["availability"] else []
                if day_name in availability:
                    filtered_providers.append(p)
            except:
                continue
        providers = filtered_providers
    
    # Convert to list if it's a tuple (from database cursor)
    providers = list(providers)
    
    # Calculate scores and sort
    for provider in providers:
        # Parse availability JSON
        try:
            provider["availability"] = json.loads(provider["availability"]) if provider["availability"] else []
        except:
            provider["availability"] = []
        
        # Calculate score: (rating × 2) + experience + (completedJobs × 0.005) - (cancellationRate × 10)
        score = (float(provider["rating"]) * 2) + provider["experience"] + (provider["completed_jobs"] * 0.005) - (float(provider["cancellation_rate"]) * 10)
        
        # Location bonus
        if location and provider["location"] == location:
            score += 1.5
        
        # Verification bonus
        if provider["is_verified"]:
            score += 0.5
            
        provider["_score"] = round(score, 2)
    
    # Sort providers
    if sort_by == "rating":
        providers.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "jobs":
        providers.sort(key=lambda x: x["completed_jobs"], reverse=True)
    elif sort_by == "experience":
        providers.sort(key=lambda x: x["experience"], reverse=True)
    elif sort_by == "response":
        providers.sort(key=lambda x: x["response_time_hours"])
    else:  # score (default)
        providers.sort(key=lambda x: x["_score"], reverse=True)
    
    return jsonify(success=True, providers=providers)


@app.route("/api/locations")
def api_locations():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT location FROM service_providers ORDER BY location")
        locations = [row["location"] for row in cur.fetchall()]
    
    return jsonify(success=True, locations=locations)


@app.route("/api/services")
def api_services():
    """Get all available service categories from database"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT service_key, service, COUNT(*) as provider_count,
                   MIN(rating) as min_rating, MAX(rating) as max_rating,
                   AVG(rating) as avg_rating
            FROM service_providers 
            GROUP BY service_key, service 
            ORDER BY service
        """)
        services = cur.fetchall()
    
    # Add service metadata
    service_data = {
        "maid": {
            "title": "Maid Service", "price": "Rs. 500 / Hour",
            "image": "https://homeworknepal.com/wp-content/uploads/2024/05/Housemaid.jpg",
            "description": "Our maids handle daily household work including sweeping, mopping, washing dishes, and basic cooking."
        },
        "cleaning": {
            "title": "Home Cleaning", "price": "Rs. 500 / Hour",
            "image": "https://sunflowermaids.com/wp-content/uploads/2021/08/Signs-of-a-Bad-Cleaning-Lady.jpg",
            "description": "Kitchens, bathrooms, bedrooms and living rooms cleaned thoroughly."
        },
        "plumber": {
            "title": "Plumber Service", "price": "Rs. 500 / Hour",
            "image": "https://nnps.com.np/wp-content/uploads/2023/06/imgs-1.jpg",
            "description": "Our plumbers fix leaking taps, blocked drains, broken pipes and bathroom fittings."
        },
        "electrician": {
            "title": "Electrician Service", "price": "Rs. 500 / Hour",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTXwC_BznDpwyR2eeQpC7mAQTTisL33B2Mt3g&s",
            "description": "Switch repairs, fan and light installations, power socket fitting, and circuit troubleshooting."
        },
        "ac": {
            "title": "AC Repair & Service", "price": "Rs. 500 / Hour",
            "image": "https://clareservices.com/wp-content/uploads/2020/07/air-conditioning-repair-service-hyderabad.jpg",
            "description": "Regular servicing, filter cleaning, gas refilling and fault repairs for all major AC brands."
        },
        "technician": {
            "title": "Technician Service", "price": "Rs. 300 / Hour",
            "image": "https://homeworknepal.com/wp-content/uploads/2022/09/electrician-electric-electricity-2755683-1024x681.jpg",
            "description": "Our technicians repair TVs, washing machines, refrigerators and microwaves."
        },
        "haircutting": {
            "title": "Hair Cutting", "price": "Rs. 200 / Person",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBOJdrtttgPWstF4HcMoxCwE8pU2dNwZEYQg&s",
            "description": "Professional haircut at home. Our barbers bring all their own tools."
        },
        "gardener": {
            "title": "Gardener Service", "price": "Rs. 1,000 / Day",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTC99OjYEYoOEna34FkVD741eZRu7AUVtSO3w&s",
            "description": "Lawn mowing, plant trimming, weeding, watering and basic garden maintenance."
        },
        "makeup": {
            "title": "Makeup Artist", "price": "Rs. 500 / Hour",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRaaYzEvMXuqWZ5Hp5Q14B9vqRFu5fQvlfBEA&s",
            "description": "Home visits for weddings, parties, photoshoots and daily events."
        },
        "photographer": {
            "title": "Photographer", "price": "Rs. 500 / Hour",
            "image": "https://img.freepik.com/free-photo/young-stylish-photographer-holds-professional-camera-taking-photos_8353-6506.jpg",
            "description": "Family events, product shoots, birthdays, ceremonies. Camera and lighting provided."
        }
    }
    
    # Enhance services with metadata
    enhanced_services = []
    for service in services:
        service_key = service["service_key"]
        metadata = service_data.get(service_key, {
            "title": service["service"],
            "price": "Rs. 500 / Hour",
            "image": "https://via.placeholder.com/300x200",
            "description": f"Professional {service['service'].lower()} service"
        })
        
        enhanced_services.append({
            "service_key": service_key,
            "service_name": service["service"],
            "provider_count": service["provider_count"],
            "avg_rating": round(float(service["avg_rating"]), 1),
            "title": metadata["title"],
            "price": metadata["price"],
            "image": metadata["image"],
            "description": metadata["description"]
        })
    
    return jsonify(success=True, services=enhanced_services)


@app.route("/api/add-sample-providers", methods=["POST"])
def add_sample_providers():
    """Add more sample providers to populate the database"""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # Additional providers for better algorithm testing
            additional_providers = [
                # More Cleaning providers
                {"name": "Maya Gurung", "service": "Home Cleaning", "service_key": "cleaning", "location": "Kathmandu", "district": "Kathmandu", "rating": 4.3, "experience": 2, "completed_jobs": 67, "cancellation_rate": 0.08, "response_time_hours": 4.0, "is_verified": False, "review_count": 34, "phone": "9801000020", "image": "https://randomuser.me/api/portraits/women/20.jpg", "availability": '["Mon","Wed","Fri"]'},
                {"name": "Kiran Shrestha", "service": "Home Cleaning", "service_key": "cleaning", "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.8, "experience": 5, "completed_jobs": 289, "cancellation_rate": 0.02, "response_time_hours": 1.5, "is_verified": True, "review_count": 145, "phone": "9801000021", "image": "https://randomuser.me/api/portraits/men/21.jpg", "availability": '["Tue","Thu","Sat","Sun"]'},
                {"name": "Sunita Rai", "service": "Home Cleaning", "service_key": "cleaning", "location": "Lalitpur", "district": "Lalitpur", "rating": 4.6, "experience": 4, "completed_jobs": 156, "cancellation_rate": 0.03, "response_time_hours": 2.5, "is_verified": True, "review_count": 78, "phone": "9801000022", "image": "https://randomuser.me/api/portraits/women/23.jpg", "availability": '["Mon","Tue","Wed","Thu","Fri"]'},
                
                # More Electrician providers
                {"name": "Bikash Tamang", "service": "Electric Repair", "service_key": "electrician", "location": "Lalitpur", "district": "Lalitpur", "rating": 4.4, "experience": 3, "completed_jobs": 123, "cancellation_rate": 0.05, "response_time_hours": 3.0, "is_verified": False, "review_count": 61, "phone": "9801000023", "image": "https://randomuser.me/api/portraits/men/24.jpg", "availability": '["Mon","Tue","Wed","Thu","Fri","Sat"]'},
                {"name": "Santosh KC", "service": "Electric Repair", "service_key": "electrician", "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.9, "experience": 8, "completed_jobs": 445, "cancellation_rate": 0.01, "response_time_hours": 1.0, "is_verified": True, "review_count": 223, "phone": "9801000024", "image": "https://randomuser.me/api/portraits/men/25.jpg", "availability": '["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'},
                {"name": "Laxmi Thapa", "service": "Electric Repair", "service_key": "electrician", "location": "Kathmandu", "district": "Kathmandu", "rating": 4.1, "experience": 1, "completed_jobs": 34, "cancellation_rate": 0.12, "response_time_hours": 5.0, "is_verified": False, "review_count": 17, "phone": "9801000025", "image": "https://randomuser.me/api/portraits/women/26.jpg", "availability": '["Wed","Thu","Fri","Sat"]'},
                
                # More Plumber providers
                {"name": "Raju Maharjan", "service": "Plumbing", "service_key": "plumber", "location": "Lalitpur", "district": "Lalitpur", "rating": 4.7, "experience": 6, "completed_jobs": 234, "cancellation_rate": 0.02, "response_time_hours": 2.0, "is_verified": True, "review_count": 117, "phone": "9801000026", "image": "https://randomuser.me/api/portraits/men/27.jpg", "availability": '["Mon","Tue","Wed","Thu","Fri"]'},
                {"name": "Kamala Lama", "service": "Plumbing", "service_key": "plumber", "location": "Kathmandu", "district": "Kathmandu", "rating": 3.9, "experience": 2, "completed_jobs": 45, "cancellation_rate": 0.15, "response_time_hours": 6.0, "is_verified": False, "review_count": 23, "phone": "9801000027", "image": "https://randomuser.me/api/portraits/women/28.jpg", "availability": '["Sat","Sun"]'},
                {"name": "Suresh Magar", "service": "Plumbing", "service_key": "plumber", "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.5, "experience": 4, "completed_jobs": 167, "cancellation_rate": 0.04, "response_time_hours": 2.5, "is_verified": True, "review_count": 84, "phone": "9801000028", "image": "https://randomuser.me/api/portraits/men/29.jpg", "availability": '["Mon","Wed","Fri","Sat","Sun"]'},
                
                # More Maid providers
                {"name": "Devi Pun", "service": "Maid Service", "service_key": "maid", "location": "Kathmandu", "district": "Kathmandu", "rating": 4.2, "experience": 3, "completed_jobs": 89, "cancellation_rate": 0.07, "response_time_hours": 3.5, "is_verified": False, "review_count": 45, "phone": "9801000029", "image": "https://randomuser.me/api/portraits/women/30.jpg", "availability": '["Mon","Tue","Wed","Thu","Fri"]'},
                {"name": "Bishnu Ghale", "service": "Maid Service", "service_key": "maid", "location": "Lalitpur", "district": "Lalitpur", "rating": 4.8, "experience": 9, "completed_jobs": 567, "cancellation_rate": 0.01, "response_time_hours": 1.0, "is_verified": True, "review_count": 284, "phone": "9801000030", "image": "https://randomuser.me/api/portraits/women/31.jpg", "availability": '["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'},
                {"name": "Tek Bahadur Rana", "service": "Maid Service", "service_key": "maid", "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.0, "experience": 1, "completed_jobs": 23, "cancellation_rate": 0.10, "response_time_hours": 4.5, "is_verified": False, "review_count": 12, "phone": "9801000031", "image": "https://randomuser.me/api/portraits/men/32.jpg", "availability": '["Tue","Thu","Sat"]'},
                
                # More AC providers
                {"name": "Nabin Karki", "service": "AC Service", "service_key": "ac", "location": "Lalitpur", "district": "Lalitpur", "rating": 4.6, "experience": 5, "completed_jobs": 178, "cancellation_rate": 0.03, "response_time_hours": 2.0, "is_verified": True, "review_count": 89, "phone": "9801000032", "image": "https://randomuser.me/api/portraits/men/33.jpg", "availability": '["Mon","Tue","Wed","Thu","Fri","Sat"]'},
                {"name": "Sarita Basnet", "service": "AC Service", "service_key": "ac", "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.3, "experience": 2, "completed_jobs": 67, "cancellation_rate": 0.06, "response_time_hours": 3.5, "is_verified": False, "review_count": 34, "phone": "9801000033", "image": "https://randomuser.me/api/portraits/women/34.jpg", "availability": '["Wed","Thu","Fri","Sat","Sun"]'},
                
                # More Technician providers
                {"name": "Gopal Adhikari", "service": "Technician Service", "service_key": "technician", "location": "Kathmandu", "district": "Kathmandu", "rating": 4.7, "experience": 6, "completed_jobs": 234, "cancellation_rate": 0.02, "response_time_hours": 1.5, "is_verified": True, "review_count": 117, "phone": "9801000034", "image": "https://randomuser.me/api/portraits/men/35.jpg", "availability": '["Mon","Tue","Wed","Thu","Fri"]'},
                {"name": "Mina Oli", "service": "Technician Service", "service_key": "technician", "location": "Lalitpur", "district": "Lalitpur", "rating": 4.1, "experience": 2, "completed_jobs": 56, "cancellation_rate": 0.08, "response_time_hours": 4.0, "is_verified": False, "review_count": 28, "phone": "9801000035", "image": "https://randomuser.me/api/portraits/women/36.jpg", "availability": '["Tue","Wed","Thu","Fri","Sat"]'},
                
                # More Hair Cutting providers
                {"name": "Arjun Limbu", "service": "Hair Cutting", "service_key": "haircutting", "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.5, "experience": 4, "completed_jobs": 145, "cancellation_rate": 0.04, "response_time_hours": 2.5, "is_verified": True, "review_count": 73, "phone": "9801000036", "image": "https://randomuser.me/api/portraits/men/37.jpg", "availability": '["Mon","Wed","Fri","Sat","Sun"]'},
                {"name": "Sabita Chhetri", "service": "Hair Cutting", "service_key": "haircutting", "location": "Lalitpur", "district": "Lalitpur", "rating": 4.8, "experience": 7, "completed_jobs": 289, "cancellation_rate": 0.02, "response_time_hours": 1.5, "is_verified": True, "review_count": 145, "phone": "9801000037", "image": "https://randomuser.me/api/portraits/women/38.jpg", "availability": '["Tue","Thu","Fri","Sat","Sun"]'},
                
                # More Gardener providers
                {"name": "Dilip Tharu", "service": "Gardener", "service_key": "gardener", "location": "Kathmandu", "district": "Kathmandu", "rating": 4.4, "experience": 5, "completed_jobs": 123, "cancellation_rate": 0.05, "response_time_hours": 3.0, "is_verified": True, "review_count": 62, "phone": "9801000038", "image": "https://randomuser.me/api/portraits/men/39.jpg", "availability": '["Mon","Tue","Wed","Thu","Fri"]'},
                {"name": "Kamana Dahal", "service": "Gardener", "service_key": "gardener", "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.1, "experience": 3, "completed_jobs": 78, "cancellation_rate": 0.07, "response_time_hours": 4.5, "is_verified": False, "review_count": 39, "phone": "9801000039", "image": "https://randomuser.me/api/portraits/women/40.jpg", "availability": '["Wed","Thu","Fri","Sat"]'},
                
                # More Makeup providers
                {"name": "Roshani Gurung", "service": "Makeup Artist", "service_key": "makeup", "location": "Lalitpur", "district": "Lalitpur", "rating": 4.6, "experience": 4, "completed_jobs": 167, "cancellation_rate": 0.03, "response_time_hours": 2.0, "is_verified": True, "review_count": 84, "phone": "9801000040", "image": "https://randomuser.me/api/portraits/women/41.jpg", "availability": '["Thu","Fri","Sat","Sun"]'},
                {"name": "Sanjay Rana", "service": "Makeup Artist", "service_key": "makeup", "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.2, "experience": 2, "completed_jobs": 89, "cancellation_rate": 0.06, "response_time_hours": 3.5, "is_verified": False, "review_count": 45, "phone": "9801000041", "image": "https://randomuser.me/api/portraits/men/42.jpg", "availability": '["Fri","Sat","Sun"]'},
                
                # More Photographer providers
                {"name": "Anil Shakya", "service": "Photographer", "service_key": "photographer", "location": "Lalitpur", "district": "Lalitpur", "rating": 4.7, "experience": 6, "completed_jobs": 234, "cancellation_rate": 0.02, "response_time_hours": 2.5, "is_verified": True, "review_count": 117, "phone": "9801000042", "image": "https://randomuser.me/api/portraits/men/43.jpg", "availability": '["Fri","Sat","Sun"]'},
                {"name": "Puja Manandhar", "service": "Photographer", "service_key": "photographer", "location": "Bhaktapur", "district": "Bhaktapur", "rating": 4.4, "experience": 3, "completed_jobs": 123, "cancellation_rate": 0.04, "response_time_hours": 3.0, "is_verified": True, "review_count": 62, "phone": "9801000043", "image": "https://randomuser.me/api/portraits/women/44.jpg", "availability": '["Sat","Sun"]'}
            ]
            
            # Insert additional providers
            for provider in additional_providers:
                cur.execute("""
                    INSERT INTO service_providers 
                    (name, service, service_key, location, district, rating, experience, 
                     completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                     review_count, image, phone, availability)
                    VALUES (%(name)s, %(service)s, %(service_key)s, %(location)s, %(district)s, 
                            %(rating)s, %(experience)s, %(completed_jobs)s, %(cancellation_rate)s, 
                            %(response_time_hours)s, %(is_verified)s, %(review_count)s, 
                            %(image)s, %(phone)s, %(availability)s)
                """, provider)
        
        conn.commit()
        return jsonify(success=True, message=f"Added {len(additional_providers)} more providers successfully!")
        
    except Exception as e:
        return jsonify(success=False, message=f"Error adding providers: {str(e)}"), 500


@app.route("/api/top-professionals")
def api_top_professionals():
    """Get top 3 rated professionals for home page"""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM service_providers 
                WHERE rating >= 4.5 AND is_verified = 1
                ORDER BY rating DESC, completed_jobs DESC, review_count DESC
                LIMIT 3
            """)
            professionals = cur.fetchall()
        
        # Convert to list and add service metadata
        professionals = list(professionals)
        for professional in professionals:
            # Parse availability JSON
            try:
                professional["availability"] = json.loads(professional["availability"]) if professional["availability"] else []
            except:
                professional["availability"] = []
        
        return jsonify(success=True, professionals=professionals)
        
    except Exception as e:
        return jsonify(success=False, message=f"Error fetching top professionals: {str(e)}"), 500


@app.route("/api/admin/providers", methods=["GET"])
def get_all_providers():
    """Get all providers for admin management"""
    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, service, service_key, location, district, rating, experience,
                       completed_jobs, cancellation_rate, response_time_hours, is_verified,
                       review_count, image, phone, availability, created_at
                FROM service_providers 
                ORDER BY created_at DESC
            """)
            providers = cur.fetchall()
        
        return jsonify(success=True, providers=providers)
    except Exception as e:
        print(f"Error in get_all_providers: {e}")
        return jsonify(success=False, message=str(e)), 500
    finally:
        if conn:
            conn.close()

@app.route("/api/admin/providers", methods=["POST"])
def add_provider():
    """Add a new provider"""
    try:
        data = request.get_json()
        
        # Map service names to keys
        service_mapping = {
            "Home Cleaning": "cleaning", "Plumbing": "plumber", "Electric Repair": "electrician",
            "AC Service": "ac", "Maid Service": "maid", "Technician Service": "technician",
            "Hair Cutting": "haircutting", "Gardener": "gardener", "Makeup Artist": "makeup",
            "Photography": "photographer"
        }
        
        service_key = service_mapping.get(data.get("service"), "other")
        
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO service_providers 
                (name, service, service_key, location, district, rating, experience,
                 completed_jobs, cancellation_rate, response_time_hours, is_verified,
                 review_count, image, phone, availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("name"),
                data.get("service"),
                service_key,
                data.get("location"),
                data.get("location"),  # district same as location
                data.get("rating", 4.0),
                data.get("experience", 1),
                0,  # completed_jobs
                0.05,  # cancellation_rate
                2.0,  # response_time_hours
                data.get("is_verified", False),
                0,  # review_count
                data.get("image") or "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
                data.get("phone"),
                '["Mon","Tue","Wed","Thu","Fri","Sat"]'  # default availability
            ))
        
        conn.commit()
        return jsonify(success=True, message="Provider added successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route("/api/admin/providers/<int:provider_id>/approve", methods=["POST"])
def approve_provider(provider_id):
    """Approve a provider and set them as verified"""
    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE service_providers 
                SET is_verified = 1
                WHERE id = %s
            """, (provider_id,))
        
        conn.commit()
        return jsonify(success=True, message="Provider approved successfully!")
    except Exception as e:
        print(f"Error approving provider: {e}")
        return jsonify(success=False, message=str(e)), 500
    finally:
        if conn:
            conn.close()

@app.route("/api/admin/providers/<int:provider_id>", methods=["PUT"])
def update_provider(provider_id):
    """Update an existing provider"""
    try:
        data = request.get_json()
        
        # Map service names to keys
        service_mapping = {
            "Home Cleaning": "cleaning", "Plumbing": "plumber", "Electric Repair": "electrician",
            "AC Service": "ac", "Maid Service": "maid", "Technician Service": "technician",
            "Hair Cutting": "haircutting", "Gardener": "gardener", "Makeup Artist": "makeup",
            "Photography": "photographer"
        }
        
        service_key = service_mapping.get(data.get("service"), "other")
        
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE service_providers 
                SET name = %s, service = %s, service_key = %s, location = %s, district = %s,
                    rating = %s, experience = %s, is_verified = %s, image = %s, phone = %s
                WHERE id = %s
            """, (
                data.get("name"),
                data.get("service"),
                service_key,
                data.get("location"),
                data.get("location"),
                data.get("rating", 4.0),
                data.get("experience", 1),
                data.get("is_verified", False),
                data.get("image") or "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
                data.get("phone"),
                provider_id
            ))
        
        conn.commit()
        return jsonify(success=True, message="Provider updated successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route("/api/admin/providers/<int:provider_id>", methods=["DELETE"])
def delete_provider(provider_id):
    """Delete a provider"""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM service_providers WHERE id = %s", (provider_id,))
        
        conn.commit()
        return jsonify(success=True, message="Provider deleted successfully!")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route("/api/admin/provider-stats", methods=["GET"])
def get_provider_stats():
    """Get provider statistics for admin dashboard"""
    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # Total providers
            cur.execute("SELECT COUNT(*) as total FROM service_providers")
            total = cur.fetchone()["total"]
            
            # Verified providers
            cur.execute("SELECT COUNT(*) as verified FROM service_providers WHERE is_verified = 1")
            verified = cur.fetchone()["verified"]
            
            # Unique services
            cur.execute("SELECT COUNT(DISTINCT service_key) as services FROM service_providers")
            services = cur.fetchone()["services"]
            
            # Average rating
            cur.execute("SELECT AVG(rating) as avg_rating FROM service_providers")
            avg_rating = round(cur.fetchone()["avg_rating"] or 0, 1)
        
        return jsonify(success=True, stats={
            "total": total,
            "verified": verified,
            "services": services,
            "avgRating": avg_rating
        })
    except Exception as e:
        print(f"Error in get_provider_stats: {e}")
        return jsonify(success=False, message=str(e)), 500
    finally:
        if conn:
            conn.close()

@app.route("/api/admin/providers/export", methods=["GET"])
def export_providers():
    """Export providers as CSV"""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, service, location, rating, experience, completed_jobs,
                       is_verified, phone, created_at
                FROM service_providers 
                ORDER BY service, name
            """)
            providers = cur.fetchall()
        
        # Create CSV content
        csv_content = "Name,Service,Location,Rating,Experience,Jobs,Verified,Phone,Created\n"
        for provider in providers:
            csv_content += f"{provider['name']},{provider['service']},{provider['location']},"
            csv_content += f"{provider['rating']},{provider['experience']},{provider['completed_jobs']},"
            csv_content += f"{'Yes' if provider['is_verified'] else 'No'},{provider['phone']},{provider['created_at']}\n"
        
        from flask import Response
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=providers.csv"}
        )
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
@app.route("/api/reset-providers", methods=["POST"])
def reset_providers():
    """Reset all providers with unique names and images for each service"""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # Clear existing providers
            cur.execute("DELETE FROM service_providers")
            
            # Nepali names
            names = [
                "Aarav Sharma", "Aashish Karki", "Abhishek Adhikari", "Aditya Bhandari", "Ajay Thapa",
                "Akash Shrestha", "Alok Poudel", "Amit Gurung", "Anil KC", "Anish Rana",
                "Arjun Basnet", "Ashok Bhattarai", "Baburam Dahal", "Bikash Giri", "Binod Joshi",
                "Bishal Rai", "Chandan Khatri", "Deepak Neupane", "Dhiraj Khadka", "Gopal Pandey",
                "Hari Koirala", "Hemant Bista", "Ishwor Acharya", "Kamal Baral", "Kiran Subedi",
                "Krishna Sigdel", "Laxman Regmi", "Madan Sapkota", "Manoj Thakuri", "Nabin Oli",
                "Naresh Bhusal", "Niraj Tiwari", "Prabin KC", "Prakash Dahal", "Ramesh Kafle",
                "Aakriti Sharma", "Aashika Karki", "Anjana Adhikari", "Anusha Bhandari", "Apsara Thapa",
                "Arati Shrestha", "Bimala Poudel", "Bina Gurung", "Chhaya KC", "Deepa Rana",
                "Gita Basnet", "Hema Bhattarai", "Indira Dahal", "Janaki Giri", "Kabita Joshi",
                "Karuna Rai", "Laxmi Khatri", "Mamata Neupane", "Manisha Khadka", "Nirmala Pandey",
                "Nisha Koirala", "Pabitra Bista", "Pramila Acharya", "Radhika Baral", "Rekha Subedi",
                "Sabita Sigdel", "Sarita Regmi", "Sharmila Sapkota", "Sita Thakuri", "Sunita Oli",
                "Sushma Bhusal", "Tara Tiwari", "Usha Kafle", "Yamuna Dahal", "Zoya Gurung"
            ]
            
            # Images
            images = [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=150&h=150&fit=crop&crop=face"
            ]
            
            # Services
            services = [
                {"key": "cleaning", "name": "Home Cleaning"},
                {"key": "plumber", "name": "Plumbing"},
                {"key": "electrician", "name": "Electric Repair"},
                {"key": "ac", "name": "AC Service"},
                {"key": "maid", "name": "Maid Service"},
                {"key": "technician", "name": "Technician Service"},
                {"key": "haircutting", "name": "Hair Cutting"},
                {"key": "gardener", "name": "Gardener"},
                {"key": "makeup", "name": "Makeup Artist"},
                {"key": "photographer", "name": "Photographer"}
            ]
            
            locations = ["Kathmandu", "Lalitpur", "Bhaktapur"]
            name_idx = 0
            image_idx = 0
            total = 0
            
            # Create unique providers for each service
            for service in services:
                for i in range(7):  # 7 providers per service
                    name = names[name_idx % len(names)]
                    image = images[image_idx % len(images)]
                    location = locations[i % len(locations)]
                    
                    # Ensure uniqueness by adding service suffix if name repeats
                    if name_idx >= len(names):
                        name = f"{name} ({service['name']})"
                    
                    cur.execute("""
                        INSERT INTO service_providers 
                        (name, service, service_key, location, district, rating, experience, 
                         completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                         review_count, image, phone, availability)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        name,
                        service["name"],
                        service["key"],
                        location,
                        location,
                        round(3.0 + (i * 0.3), 1),  # Rating 3.0-4.8
                        (i % 5) + 1,  # Experience 1-5
                        50 + (i * 30),  # Jobs 50-230
                        round(0.02 + (i * 0.01), 2),  # Cancel rate
                        1.5 + (i * 0.5),  # Response time
                        i % 2 == 0,  # Verified every other
                        25 + (i * 15),  # Reviews
                        image,
                        f"980{1000000 + total:07d}",  # Unique phone
                        '["Mon","Tue","Wed","Thu","Fri","Sat"]'
                    ))
                    
                    name_idx += 1
                    image_idx += 1
                    total += 1
        
        conn.commit()
        return jsonify(success=True, message=f"Created {total} unique providers across all services!")
        
    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}"), 500
@app.route("/api/update-provider-data", methods=["POST"])
def update_provider_data():
    """Update provider ratings and images to be more diverse and Nepali-looking"""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # First, clear existing providers to start fresh
            cur.execute("DELETE FROM service_providers")
            
            # Authentic Nepali names from the provided list
            male_names = [
                "Aarav Sharma", "Aashish Karki", "Abhishek Adhikari", "Aditya Bhandari", "Ajay Thapa",
                "Akash Shrestha", "Alok Poudel", "Amit Gurung", "Anil KC", "Anish Rana",
                "Arjun Basnet", "Ashok Bhattarai", "Baburam Dahal", "Bikash Giri", "Binod Joshi",
                "Bishal Rai", "Chandan Khatri", "Deepak Neupane", "Dhiraj Khadka", "Gopal Pandey",
                "Hari Koirala", "Hemant Bista", "Ishwor Acharya", "Kamal Baral", "Kiran Subedi",
                "Krishna Sigdel", "Laxman Regmi", "Madan Sapkota", "Manoj Thakuri", "Nabin Oli",
                "Naresh Bhusal", "Niraj Tiwari", "Prabin KC", "Prakash Dahal", "Ramesh Kafle"
            ]
            
            female_names = [
                "Aakriti Sharma", "Aashika Karki", "Anjana Adhikari", "Anusha Bhandari", "Apsara Thapa",
                "Arati Shrestha", "Bimala Poudel", "Bina Gurung", "Chhaya KC", "Deepa Rana",
                "Gita Basnet", "Hema Bhattarai", "Indira Dahal", "Janaki Giri", "Kabita Joshi",
                "Karuna Rai", "Laxmi Khatri", "Mamata Neupane", "Manisha Khadka", "Nirmala Pandey",
                "Nisha Koirala", "Pabitra Bista", "Pramila Acharya", "Radhika Baral", "Rekha Subedi",
                "Sabita Sigdel", "Sarita Regmi", "Sharmila Sapkota", "Sita Thakuri", "Sunita Oli",
                "Sushma Bhusal", "Tara Tiwari", "Usha Kafle", "Yamuna Dahal", "Zoya Gurung"
            ]
            
            # Combine all names
            all_names = male_names + female_names
            
            # Professional images from different sources
            image_urls = [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1566492031773-4f4e44671d66?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1520813792240-56fc4a3765a7?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1499952127939-9bbf5af6c51c?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1496345875659-11f7dd282d1d?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1521119989659-a83eee488004?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1522556189639-b150ed9c4330?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1527980965255-d3b416303d12?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1558203728-00f45181dd84?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1548142813-c348350df52b?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1554151228-14d9def656e4?w=150&h=150&fit=crop&crop=face",
                "https://images.unsplash.com/photo-1557862921-37829c790f19?w=150&h=150&fit=crop&crop=face"
            ]
            
            # Service categories with their details
            services = [
                {"key": "cleaning", "name": "Home Cleaning", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]},
                {"key": "plumber", "name": "Plumbing", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]},
                {"key": "electrician", "name": "Electric Repair", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]},
                {"key": "ac", "name": "AC Service", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]},
                {"key": "maid", "name": "Maid Service", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]},
                {"key": "technician", "name": "Technician Service", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]},
                {"key": "haircutting", "name": "Hair Cutting", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]},
                {"key": "gardener", "name": "Gardener", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]},
                {"key": "makeup", "name": "Makeup Artist", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]},
                {"key": "photographer", "name": "Photographer", "locations": ["Kathmandu", "Lalitpur", "Bhaktapur"]}
            ]
            
            # Shuffle names and images for randomness
            import random
            random.shuffle(all_names)
            random.shuffle(image_urls)
            
            total_providers = 0
            name_index = 0
            image_index = 0
            
            # Create 6-8 providers per service category
            for service in services:
                providers_per_service = random.randint(6, 8)
                
                for i in range(providers_per_service):
                    # Get unique name and image
                    name = all_names[name_index % len(all_names)]
                    image = image_urls[image_index % len(image_urls)]
                    location = service["locations"][i % len(service["locations"])]
                    
                    # Generate diverse stats
                    rating = round(random.uniform(3.0, 5.0), 1)
                    experience = random.randint(1, 8)
                    completed_jobs = random.randint(15, 500)
                    cancellation_rate = round(random.uniform(0.0, 0.15), 3)
                    response_time = round(random.uniform(1.0, 6.0), 1)
                    is_verified = random.choice([True, False, True])  # 2/3 chance of being verified
                    review_count = random.randint(5, 250)
                    
                    # Availability days
                    all_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    num_days = random.randint(4, 7)
                    availability = random.sample(all_days, num_days)
                    
                    # Insert provider
                    cur.execute("""
                        INSERT INTO service_providers 
                        (name, service, service_key, location, district, rating, experience, 
                         completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                         review_count, image, phone, availability)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        name,
                        service["name"],
                        service["key"],
                        location,
                        location,  # district same as location
                        rating,
                        experience,
                        completed_jobs,
                        cancellation_rate,
                        response_time,
                        is_verified,
                        review_count,
                        image,
                        f"980{random.randint(1000000, 9999999)}",  # Random phone
                        json.dumps(availability)
                    ))
                    
                    total_providers += 1
                    name_index += 1
                    image_index += 1
        
        conn.commit()
        return jsonify(success=True, message=f"Created {total_providers} unique providers across all service categories with authentic Nepali names!")
        
    except Exception as e:
        return jsonify(success=False, message=f"Error updating provider data: {str(e)}"), 500


@app.route("/api/register-provider", methods=["POST"])
def register_provider():
    """Register a new service provider with optional image upload"""
    try:
        # Handle both JSON and form data
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Form data with file upload
            data = request.form.to_dict()
            if 'availability' in data:
                data['availability'] = json.loads(data['availability'])
            image_file = request.files.get('image')
        else:
            # JSON data (backward compatibility)
            data = request.get_json(silent=True) or {}
            image_file = None
        
        # Validate required fields
        required_fields = ["name", "service", "location", "phone", "experience"]
        for field in required_fields:
            if not data.get(field):
                return jsonify(success=False, message=f"{field.title()} is required"), 400
        
        # Validate email and password if provided
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()
        
        if email and password:
            if len(password) < 6:
                return jsonify(success=False, message="Password must be at least 6 characters"), 400
        
        # Validate phone number
        phone = data.get("phone", "").strip()
        if not phone.startswith("98") or len(phone) != 10:
            return jsonify(success=False, message="Phone number must be 10 digits starting with 98"), 400
        
        # Validate and save image if provided
        image_url = None
        if image_file and image_file.filename:
            # Validate file size
            if len(image_file.read()) > MAX_FILE_SIZE:
                return jsonify(success=False, message="Image size must be less than 2MB"), 400
            
            # Reset file pointer after reading
            image_file.seek(0)
            
            # Validate file type
            if not allowed_file(image_file.filename):
                return jsonify(success=False, message="Only JPG and PNG images are allowed"), 400
            
            # Save image
            image_url = save_provider_image(image_file)
            if not image_url:
                return jsonify(success=False, message="Failed to save image"), 500
        
        # Map service names to service keys
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
        
        service_name = data.get("service")
        if service_name not in service_mapping:
            return jsonify(success=False, message="Invalid service selected"), 400
        
        service_info = service_mapping[service_name]
        
        # Parse availability days
        availability_days = data.get("availability", [])
        if not availability_days:
            availability_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]  # Default weekdays + Saturday
        
        # Use uploaded image or default
        final_image_url = image_url or "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"
        
        # Create new provider record
        conn = get_db()
        with conn.cursor() as cur:
            # Check if phone number already exists
            cur.execute("SELECT id FROM service_providers WHERE phone = %s", (phone,))
            if cur.fetchone():
                return jsonify(success=False, message="Phone number already registered"), 400
            
            # Check if email column exists and email already exists (if provided)
            if email:
                try:
                    cur.execute("SELECT id FROM service_providers WHERE email = %s", (email,))
                    if cur.fetchone():
                        return jsonify(success=False, message="Email already registered"), 400
                except pymysql.err.OperationalError as e:
                    if "Unknown column 'email'" in str(e):
                        # Email column doesn't exist yet, skip email check
                        print("Warning: email column doesn't exist yet, skipping email validation")
                    else:
                        raise e
            
            # Hash password if provided
            hashed_password = generate_password_hash(password) if password else None
            
            # Try to insert with email/password columns, fallback if they don't exist
            try:
                cur.execute("""
                    INSERT INTO service_providers 
                    (name, service, service_key, location, district, rating, experience, 
                     completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                     review_count, image, phone, availability, email, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data.get("name").strip(),
                    service_info["name"],
                    service_info["key"],
                    data.get("location").strip(),
                    data.get("location").strip(),  # district same as location for now
                    3.5,  # Starting rating for new providers
                    int(data.get("experience", 0)),
                    0,    # No completed jobs initially
                    0.0,  # No cancellation rate initially
                    4.0,  # Default response time
                    False,  # Not verified initially
                    0,    # No reviews initially
                    final_image_url,
                    phone,
                    json.dumps(availability_days),
                    email if email else None,
                    hashed_password
                ))
            except pymysql.err.OperationalError as e:
                if "Unknown column" in str(e):
                    # Fallback to old schema without email/password columns
                    print("Warning: Using fallback insert without email/password columns")
                    cur.execute("""
                        INSERT INTO service_providers 
                        (name, service, service_key, location, district, rating, experience, 
                         completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                         review_count, image, phone, availability)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        data.get("name").strip(),
                        service_info["name"],
                        service_info["key"],
                        data.get("location").strip(),
                        data.get("location").strip(),  # district same as location for now
                        3.5,  # Starting rating for new providers
                        int(data.get("experience", 0)),
                        0,    # No completed jobs initially
                        0.0,  # No cancellation rate initially
                        4.0,  # Default response time
                        False,  # Not verified initially
                        0,    # No reviews initially
                        final_image_url,
                        phone,
                        json.dumps(availability_days)
                    ))
                else:
                    raise e
            
            provider_id = cur.lastrowid
        
        conn.commit()
        
        # Determine redirect URL based on whether email/password was provided and columns exist
        redirect_url = "/services"  # Default fallback
        success_message = "Registration successful! You will appear in provider listings."
        
        if email and password:
            # Check if we successfully stored email/password (columns exist)
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT email FROM service_providers WHERE id = %s", (provider_id,))
                    result = cur.fetchone()
                    if result and result.get('email'):
                        redirect_url = "/provider/login"
                        success_message = "Registration successful! Please login to access your provider portal."
            except:
                # Email column doesn't exist, use default redirect
                pass
        
        return jsonify(
            success=True, 
            message=success_message,
            provider_id=provider_id,
            redirect_url=redirect_url
        )
        
    except Exception as e:
        return jsonify(success=False, message=f"Registration failed: {str(e)}"), 500


# ─────────────────────────────────────────────
# ESEWA PAYMENT
# ─────────────────────────────────────────────
def generate_esewa_signature(total_amount, transaction_uuid, product_code):
    """Generate HMAC SHA256 signature for eSewa v2 — values must be strings"""
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = hmac.new(
        ESEWA_SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode("utf-8")


@app.route("/api/esewa/initiate", methods=["POST"])
def esewa_initiate():
    data       = request.get_json(silent=True) or {}
    booking_id = data.get("booking_id")
    order      = get_order(booking_id)

    if not order:
        return jsonify(success=False, message="Order not found"), 404

    amount     = SERVICE_PRICES.get(order.get("service"), 500)
    amount_str = str(amount)          # ← must be plain string, no decimals
    base_url   = os.environ.get("BASE_URL", request.host_url.rstrip("/"))

    signature  = generate_esewa_signature(amount_str, booking_id, ESEWA_MERCHANT_CODE)

    return jsonify(
        success=True,
        merchant_code=ESEWA_MERCHANT_CODE,
        amount=amount_str,
        booking_id=booking_id,
        signature=signature,
        success_url=base_url + "/payment/success",
        failure_url=base_url + "/payment/failure",
        esewa_url=ESEWA_BASE_URL + "/api/epay/main/v2/form"
    )


@app.route("/payment/success")
def payment_success():
    """
    eSewa v2 sends a base64-encoded JSON as ?data=...
    Decode it to get transaction_uuid (our booking_id) and status.
    """
    booking_id = None
    status     = None
    payment_ok = False

    encoded = request.args.get("data")
    if encoded:
        try:
            # Add padding if needed
            padding = 4 - len(encoded) % 4
            if padding != 4:
                encoded += "=" * padding
            decoded = json.loads(base64.b64decode(encoded).decode("utf-8"))
            booking_id = decoded.get("transaction_uuid")
            status     = decoded.get("status")
        except Exception:
            pass

    # Fallback for older eSewa or manual testing
    if not booking_id:
        booking_id = request.args.get("transaction_uuid") or request.args.get("purchase_order_id")
        status     = request.args.get("status", "COMPLETE")

    if booking_id and status == "COMPLETE":
        update_order_field(booking_id, payment="paid", status="confirmed")
        payment_ok = True

    return render_template("payment_success.html", booking_id=booking_id, payment_ok=payment_ok)


@app.route("/payment/failure")
def payment_failure():
    booking_id = request.args.get("transaction_uuid", "")
    return render_template("payment_failure.html", booking_id=booking_id)


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("🚀 NepSewa server starting...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📍 Health check: http://127.0.0.1:8000/health")
    print("📍 Services page: http://127.0.0.1:8000/services")
    app.run(debug=True, host='127.0.0.1', port=8000)