#!/usr/bin/env python3
"""
Reset database with new locations
"""

import pymysql
from main import DB_CONFIG

def reset_database():
    print("🔄 Resetting database with new locations...")
    
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        # Drop and recreate the service_providers table
        print("🗑️ Dropping old providers table...")
        cur.execute("DROP TABLE IF EXISTS service_providers")
        
        # Recreate table
        print("🏗️ Creating new providers table...")
        cur.execute("""
            CREATE TABLE service_providers (
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
        
        # Insert new sample data with updated locations
        print("📍 Inserting providers with new locations...")
        providers = [
            ("Ram Bahadur", "Electric Repair", "electrician", "Butwal", "Rupandehi", 4.8, 5, 312, 0.02, 1.5, True, 148, "9801000001", "https://randomuser.me/api/portraits/men/32.jpg", '["Mon","Tue","Wed","Thu","Fri","Sat"]'),
            ("Sita Lama", "Home Cleaning", "cleaning", "Tilottama", "Rupandehi", 4.9, 6, 420, 0.01, 1.0, True, 210, "9801000002", "https://randomuser.me/api/portraits/women/44.jpg", '["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'),
            ("Hari Sharma", "Plumbing", "plumber", "Bhairahawa", "Rupandehi", 4.7, 4, 198, 0.03, 2.0, True, 95, "9801000003", "https://randomuser.me/api/portraits/men/76.jpg", '["Mon","Tue","Wed","Thu","Fri"]'),
            ("Gita KC", "Spa & Massage", "makeup", "Chitwan", "Chitwan", 5.0, 4, 175, 0.00, 2.5, True, 88, "9801000004", "https://randomuser.me/api/portraits/women/65.jpg", '["Tue","Wed","Thu","Fri","Sat","Sun"]'),
            ("Ramesh Tamang", "Hair Cutting", "haircutting", "Butwal", "Rupandehi", 4.2, 2, 89, 0.07, 3.0, False, 42, "9801000005", "https://randomuser.me/api/portraits/men/55.jpg", '["Mon","Wed","Fri","Sat","Sun"]'),
            ("Suman Rai", "Home Cleaning", "cleaning", "Tilottama", "Rupandehi", 4.7, 3, 134, 0.04, 2.0, True, 67, "9801000006", "https://randomuser.me/api/portraits/men/66.jpg", '["Mon","Tue","Thu","Fri","Sat"]'),
            ("Binod KC", "AC Service", "ac", "Bhairahawa", "Rupandehi", 4.5, 4, 220, 0.03, 2.0, True, 110, "9801000007", "https://randomuser.me/api/portraits/men/88.jpg", '["Mon","Tue","Wed","Thu","Fri","Sat"]'),
            ("Anita Thapa", "Maid Service", "maid", "Chitwan", "Chitwan", 4.6, 7, 380, 0.02, 1.5, True, 190, "9801000008", "https://randomuser.me/api/portraits/women/33.jpg", '["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]'),
            ("Deepak Gurung", "Plumbing", "plumber", "Butwal", "Rupandehi", 4.4, 3, 112, 0.05, 3.5, False, 55, "9801000009", "https://randomuser.me/api/portraits/men/41.jpg", '["Tue","Wed","Fri","Sat"]'),
            ("Priya Shrestha", "Makeup Artist", "makeup", "Tilottama", "Rupandehi", 4.8, 5, 260, 0.02, 2.0, True, 130, "9801000010", "https://randomuser.me/api/portraits/women/58.jpg", '["Mon","Wed","Thu","Fri","Sat","Sun"]'),
            ("Rajesh Pandey", "Gardener", "gardener", "Bhairahawa", "Rupandehi", 4.3, 6, 145, 0.06, 4.0, False, 72, "9801000011", "https://randomuser.me/api/portraits/men/62.jpg", '["Mon","Tue","Thu","Sat","Sun"]'),
            ("Nisha Maharjan", "Photographer", "photographer", "Chitwan", "Chitwan", 4.9, 8, 310, 0.01, 3.0, True, 155, "9801000012", "https://randomuser.me/api/portraits/women/22.jpg", '["Fri","Sat","Sun"]')
        ]
        
        for provider in providers:
            cur.execute("""
                INSERT INTO service_providers 
                (name, service, service_key, location, district, rating, experience, 
                 completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                 review_count, phone, image, availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, provider)
    
    conn.commit()
    conn.close()
    print("✅ Database reset complete with new locations!")
    print("📍 New locations: Butwal, Tilottama, Bhairahawa, Chitwan")

if __name__ == "__main__":
    reset_database()