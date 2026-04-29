#!/usr/bin/env python3
"""
NepSewa Server Startup Script
This script helps diagnose and run the NepSewa Flask application
"""

import sys
import os
import pymysql
from main import app, DB_CONFIG, init_db

def check_database():
    """Check if database connection is working"""
    print("🔍 Checking database connection...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ Database connection successful!")
        
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
            print(f"📊 Found {len(tables)} tables in database")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure MySQL is running")
        print("2. Check if database 'nepsewa' exists")
        print("3. Verify username/password in main.py")
        print("4. Try: CREATE DATABASE nepsewa;")
        return False

def check_templates():
    """Check if template files exist"""
    print("\n🔍 Checking template files...")
    template_dir = "templates"
    required_templates = ["nepsewa.html", "services.html", "login.html"]
    
    if not os.path.exists(template_dir):
        print(f"❌ Templates directory '{template_dir}' not found!")
        return False
    
    missing_templates = []
    for template in required_templates:
        template_path = os.path.join(template_dir, template)
        if os.path.exists(template_path):
            print(f"✅ {template} found")
        else:
            print(f"❌ {template} missing")
            missing_templates.append(template)
    
    return len(missing_templates) == 0

def main():
    print("🚀 NepSewa Server Startup")
    print("=" * 40)
    
    # Check database
    db_ok = check_database()
    
    # Check templates
    templates_ok = check_templates()
    
    if not db_ok:
        print("\n❌ Cannot start server - database issues")
        sys.exit(1)
    
    if not templates_ok:
        print("\n❌ Cannot start server - missing templates")
        sys.exit(1)
    
    print("\n🔧 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    print("\n🌐 Starting Flask server...")
    print("📍 Local access: http://127.0.0.1:8001")
    print("📍 Network access: http://[your-ip]:8001")
    print("📍 Health check: http://127.0.0.1:8001/health")
    print("📍 Services page: http://127.0.0.1:8001/services")
    print("\n💡 To access from other devices:")
    print("   1. Find your IP: Run 'ifconfig' (Mac/Linux) or 'ipconfig' (Windows)")
    print("   2. Use: http://[your-ip]:8001")
    print("   3. Make sure devices are on same WiFi network")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=8001)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()