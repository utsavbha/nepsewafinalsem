#!/usr/bin/env python3
"""
MySQL Configuration for NepSewa Local Development
"""

# MySQL Configuration — used by main.py for local runs (unless DB_* env vars are set).
# On macOS, root almost always has a password: put yours below (same as mysql -u root -p).
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'nepsewa123',  # Set your MySQL root password here
    'database': 'nepsewa_db',
    'port': 3306
}

def get_mysql_connection():
    """Get MySQL connection"""
    try:
        import mysql.connector
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        conn.autocommit = True
        print("✅ Connected to MySQL database")
        return conn
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return None

def setup_mysql_database():
    """Setup MySQL database and tables"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(180) NOT NULL UNIQUE,
                password VARCHAR(256) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create service providers table (aligned with main.py init_db)
        cursor.execute("""
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
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ MySQL database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ MySQL setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_mysql_database()