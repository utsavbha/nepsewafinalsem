#!/usr/bin/env python3
"""Fix database schema for NepSewa"""
import pymysql

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'nepsewa_db',
    'port': 3306
}

def fix_database():
    try:
        # Connect to MySQL
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port'],
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cur:
            # Create database if it doesn't exist
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            print(f"✅ Database '{DB_CONFIG['database']}' ready")
            
        conn.close()
        
        # Reconnect to the specific database
        conn = pymysql.connect(**DB_CONFIG, autocommit=True, cursorclass=pymysql.cursors.DictCursor)
        
        with conn.cursor() as cur:
            # Disable foreign key checks temporarily
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Drop and recreate users table with correct schema
            print("🔄 Recreating users table...")
            cur.execute("DROP TABLE IF EXISTS users")
            cur.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(120) NOT NULL,
                    email VARCHAR(180) NOT NULL UNIQUE,
                    password VARCHAR(256) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Users table created")
            
            # Re-enable foreign key checks
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            # Ensure service_providers table exists with correct schema
            print("🔄 Checking service_providers table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS service_providers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(120) NOT NULL,
                    service VARCHAR(100) NOT NULL,
                    service_key VARCHAR(50) NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    district VARCHAR(100) NOT NULL,
                    latitude DECIMAL(10,8) DEFAULT NULL,
                    longitude DECIMAL(11,8) DEFAULT NULL,
                    rating DECIMAL(3,2) DEFAULT 0.0,
                    experience INT DEFAULT 0,
                    completed_jobs INT DEFAULT 0,
                    cancellation_rate DECIMAL(4,3) DEFAULT 0.0,
                    response_time_hours DECIMAL(4,1) DEFAULT 24.0,
                    is_verified BOOLEAN DEFAULT FALSE,
                    review_count INT DEFAULT 0,
                    image TEXT,
                    phone VARCHAR(15),
                    availability JSON,
                    email VARCHAR(180) NULL,
                    password VARCHAR(256),
                    bio TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_service_providers_email (email)
                )
            """)
            print("✅ Service providers table ready")
            
            # Create indexes
            print("🔄 Creating indexes...")
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_service_key ON service_providers (service_key)",
                "CREATE INDEX IF NOT EXISTS idx_location ON service_providers (location)",
                "CREATE INDEX IF NOT EXISTS idx_rating ON service_providers (rating)",
                "CREATE INDEX IF NOT EXISTS idx_email ON service_providers (email)",
            ]
            
            for idx_sql in indexes:
                try:
                    cur.execute(idx_sql)
                except Exception as e:
                    if "Duplicate key name" not in str(e):
                        print(f"⚠️  Index warning: {e}")
            
            print("✅ Indexes created")
            
        conn.close()
        print("\n🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_database()
