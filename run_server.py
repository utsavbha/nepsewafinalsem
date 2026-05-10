#!/usr/bin/env python3
"""
NepSewa Production Server for Render Deployment
"""

import os
import sys
import pymysql
from main import app, init_db

def get_db_config():
    """Get database configuration from environment variables"""
    # For Render deployment, use environment variables
    if os.environ.get('DATABASE_URL'):
        # Parse DATABASE_URL format: mysql://user:password@host:port/database
        import urllib.parse as urlparse
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        return {
            'host': url.hostname,
            'port': url.port or 3306,
            'user': url.username,
            'password': url.password,
            'database': url.path[1:],  # Remove leading slash
            'autocommit': True,
            'cursorclass': pymysql.cursors.DictCursor
        }
    else:
        # Local development fallback
        return {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD', 'nepsewa123'),
            'database': os.environ.get('DB_NAME', 'nepsewa'),
            'autocommit': True,
            'cursorclass': pymysql.cursors.DictCursor
        }

def check_database():
    """Check database connection with production config"""
    print("🔍 Checking database connection...")
    try:
        db_config = get_db_config()
        conn = pymysql.connect(**db_config)
        print("✅ Database connection successful!")
        
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
            print(f"📊 Found {len(tables)} tables in database")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def setup_production_db():
    """Setup database configuration for production"""
    # Update main.py DB_CONFIG for production
    from main import DB_CONFIG
    production_config = get_db_config()
    DB_CONFIG.update(production_config)
    print("✅ Production database configuration applied")

def main():
    """Main server startup function"""
    print("🚀 NepSewa Production Server")
    print("=" * 50)
    
    # Setup production database configuration
    setup_production_db()
    
    # Check database connection
    if not check_database():
        print("❌ Database connection failed - server cannot start")
        sys.exit(1)
    
    # Initialize database
    print("\n🔧 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't exit on init failure in production - tables might already exist
        print("⚠️  Continuing anyway - tables might already exist")
    
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get('PORT', 8001))
    
    print(f"\n🌐 Starting production server on port {port}...")
    print("📍 Health check: /health")
    print("📍 Services page: /services")
    print("=" * 50)
    
    # Run in production mode
    try:
        app.run(
            debug=False,  # Disable debug in production
            host='0.0.0.0',  # Listen on all interfaces
            port=port,
            threaded=True  # Enable threading for better performance
        )
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()