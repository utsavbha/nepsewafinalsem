#!/usr/bin/env python3
"""
Interactive MySQL Setup for NepSewa
This script will prompt for your MySQL password
"""

import mysql.connector
import getpass

def setup_mysql_interactive():
    """Setup MySQL database with interactive password input"""
    try:
        # Get MySQL password from user
        print("🔐 MySQL Setup for NepSewa")
        password = getpass.getpass("Enter your MySQL root password: ")
        
        # MySQL Configuration
        config = {
            'host': 'localhost',
            'user': 'root',
            'password': password,
            'database': 'nepsewa_db',
            'port': 3306
        }
        
        # Connect to MySQL
        print("🔌 Connecting to MySQL...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("🚀 Setting up MySQL database...")
        
        # Drop existing tables to start fresh
        cursor.execute("DROP TABLE IF EXISTS service_providers")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(180) NOT NULL UNIQUE,
                password VARCHAR(256) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create service providers table
        cursor.execute("""
            CREATE TABLE service_providers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                service VARCHAR(100) NOT NULL,
                service_key VARCHAR(50) NOT NULL,
                location VARCHAR(100) NOT NULL,
                district VARCHAR(100) NOT NULL,
                latitude DECIMAL(10,8) DEFAULT NULL,
                longitude DECIMAL(11,8) DEFAULT NULL,
                rating DECIMAL(3,2) DEFAULT 4.0,
                experience INT DEFAULT 1,
                completed_jobs INT DEFAULT 0,
                cancellation_rate DECIMAL(4,3) DEFAULT 0.0,
                response_time_hours DECIMAL(4,1) DEFAULT 2.0,
                is_verified BOOLEAN DEFAULT TRUE,
                review_count INT DEFAULT 0,
                image TEXT,
                phone VARCHAR(15),
                availability JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("✅ Tables created successfully")
        
        # Add comprehensive provider data (30+ providers, 15+ per service)
        providers = [
            # Home Cleaning Providers (15)
            ("Aarav Sharma", "Home Cleaning", "cleaning", "Butwal", "Rupandehi", 27.7012, 83.4523, 4.8, 5, 312, 0.02, 1.5, True, 148, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face", "9801000001"),
            ("Sita Lama", "Home Cleaning", "cleaning", "Tilottama", "Rupandehi", 27.7189, 83.4287, 4.9, 6, 420, 0.01, 1.0, True, 210, "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face", "9801000002"),
            ("Maya Gurung", "Home Cleaning", "cleaning", "Bhairahawa", "Rupandehi", 27.5095, 83.4534, 4.3, 2, 67, 0.08, 4.0, False, 34, "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face", "9801000003"),
            ("Kamala Rai", "Home Cleaning", "cleaning", "Chitwan", "Chitwan", 27.5278, 84.3567, 4.7, 4, 198, 0.03, 2.0, True, 95, "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face", "9801000004"),
            ("Sunita Thapa", "Home Cleaning", "cleaning", "Butwal", "Rupandehi", 27.7023, 83.4489, 4.6, 3, 156, 0.05, 2.5, True, 78, "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face", "9801000005"),
            ("Devi Sharma", "Home Cleaning", "cleaning", "Tilottama", "Rupandehi", 27.7156, 83.4298, 4.5, 2, 89, 0.07, 3.0, False, 42, "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face", "9801000006"),
            ("Gita Neupane", "Home Cleaning", "cleaning", "Bhairahawa", "Rupandehi", 27.5089, 83.4487, 4.8, 7, 289, 0.02, 1.5, True, 145, "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face", "9801000007"),
            ("Mina Oli", "Home Cleaning", "cleaning", "Chitwan", "Chitwan", 27.5312, 84.3523, 4.4, 3, 123, 0.05, 3.0, False, 61, "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face", "9801000008"),
            ("Radha KC", "Home Cleaning", "cleaning", "Butwal", "Rupandehi", 27.6998, 83.4512, 4.9, 8, 345, 0.01, 1.0, True, 172, "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face", "9801000009"),
            ("Sarita Tamang", "Home Cleaning", "cleaning", "Tilottama", "Rupandehi", 27.7201, 83.4334, 4.2, 1, 45, 0.09, 4.0, False, 22, "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=150&h=150&fit=crop&crop=face", "9801000010"),
            ("Laxmi Rana", "Home Cleaning", "cleaning", "Bhairahawa", "Rupandehi", 27.5067, 83.4501, 4.7, 5, 234, 0.03, 2.0, True, 117, "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=150&h=150&fit=crop&crop=face", "9801000011"),
            ("Parvati Joshi", "Home Cleaning", "cleaning", "Chitwan", "Chitwan", 27.5289, 84.3578, 4.6, 4, 178, 0.04, 2.5, True, 89, "https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?w=150&h=150&fit=crop&crop=face", "9801000012"),
            ("Shanti Basnet", "Home Cleaning", "cleaning", "Butwal", "Rupandehi", 27.7034, 83.4456, 4.3, 2, 67, 0.08, 3.5, False, 33, "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=150&h=150&fit=crop&crop=face", "9801000013"),
            ("Urmila Pandey", "Home Cleaning", "cleaning", "Tilottama", "Rupandehi", 27.7145, 83.4323, 4.8, 6, 267, 0.02, 1.8, True, 134, "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=150&h=150&fit=crop&crop=face", "9801000014"),
            ("Bishnu Ghale", "Home Cleaning", "cleaning", "Bhairahawa", "Rupandehi", 27.5112, 83.4467, 4.5, 3, 112, 0.06, 2.8, True, 56, "https://images.unsplash.com/photo-1566492031773-4f4e44671d66?w=150&h=150&fit=crop&crop=face", "9801000015"),
            
            # Plumbing Providers (15)
            ("Arjun Basnet", "Plumbing", "plumber", "Butwal", "Rupandehi", 27.6987, 83.4478, 4.7, 4, 198, 0.03, 2.0, True, 95, "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face", "9801000016"),
            ("Hari Sharma", "Plumbing", "plumber", "Tilottama", "Rupandehi", 27.7234, 83.4312, 4.5, 3, 156, 0.05, 2.5, True, 78, "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face", "9801000017"),
            ("Raju Maharjan", "Plumbing", "plumber", "Chitwan", "Chitwan", 27.5278, 84.3567, 4.6, 6, 234, 0.02, 2.0, True, 117, "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face", "9801000018"),
            ("Bikash Tamang", "Plumbing", "plumber", "Bhairahawa", "Rupandehi", 27.5095, 83.4534, 4.8, 7, 289, 0.01, 1.5, True, 145, "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face", "9801000019"),
            ("Nabin Karki", "Plumbing", "plumber", "Butwal", "Rupandehi", 27.7012, 83.4523, 4.4, 2, 89, 0.07, 3.0, False, 42, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face", "9801000020"),
            ("Gopal Adhikari", "Plumbing", "plumber", "Tilottama", "Rupandehi", 27.7189, 83.4287, 4.9, 8, 345, 0.01, 1.0, True, 172, "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&h=150&fit=crop&crop=face", "9801000021"),
            ("Deepak Gurung", "Plumbing", "plumber", "Chitwan", "Chitwan", 27.5312, 84.3523, 4.3, 1, 45, 0.09, 4.0, False, 22, "https://images.unsplash.com/photo-1499952127939-9bbf5af6c51c?w=150&h=150&fit=crop&crop=face", "9801000022"),
            ("Suresh Rai", "Plumbing", "plumber", "Bhairahawa", "Rupandehi", 27.5067, 83.4501, 4.7, 5, 234, 0.03, 2.0, True, 117, "https://images.unsplash.com/photo-1496345875659-11f7dd282d1d?w=150&h=150&fit=crop&crop=face", "9801000023"),
            ("Ramesh Thapa", "Plumbing", "plumber", "Butwal", "Rupandehi", 27.7023, 83.4489, 4.6, 4, 178, 0.04, 2.5, True, 89, "https://images.unsplash.com/photo-1521119989659-a83eee488004?w=150&h=150&fit=crop&crop=face", "9801000024"),
            ("Binod KC", "Plumbing", "plumber", "Tilottama", "Rupandehi", 27.7156, 83.4298, 4.2, 2, 67, 0.08, 3.5, False, 33, "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=150&h=150&fit=crop&crop=face", "9801000025"),
            ("Mahesh Oli", "Plumbing", "plumber", "Chitwan", "Chitwan", 27.5289, 84.3578, 4.8, 6, 267, 0.02, 1.8, True, 134, "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150&h=150&fit=crop&crop=face", "9801000026"),
            ("Santosh Pandey", "Plumbing", "plumber", "Bhairahawa", "Rupandehi", 27.5089, 83.4487, 4.5, 3, 112, 0.06, 2.8, True, 56, "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face", "9801000027"),
            ("Kiran Joshi", "Plumbing", "plumber", "Butwal", "Rupandehi", 27.7034, 83.4456, 4.9, 9, 456, 0.01, 1.2, True, 228, "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=150&h=150&fit=crop&crop=face", "9801000028"),
            ("Prakash Neupane", "Plumbing", "plumber", "Tilottama", "Rupandehi", 27.7145, 83.4323, 4.4, 3, 134, 0.05, 2.7, True, 67, "https://images.unsplash.com/photo-1520813792240-56fc4a3765a7?w=150&h=150&fit=crop&crop=face", "9801000029"),
            ("Rajesh Ghale", "Plumbing", "plumber", "Chitwan", "Chitwan", 27.5323, 84.3545, 4.7, 5, 189, 0.03, 2.1, True, 94, "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=150&h=150&fit=crop&crop=face", "9801000030"),
            
            # Electrician Providers (15)
            ("Deepa Rana", "Electric Repair", "electrician", "Bhairahawa", "Rupandehi", 27.5067, 83.4501, 5.0, 4, 175, 0.00, 2.5, True, 88, "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&h=150&fit=crop&crop=face", "9801000031"),
            ("Ram Bahadur", "Electric Repair", "electrician", "Butwal", "Rupandehi", 27.7023, 83.4489, 4.8, 5, 312, 0.02, 1.5, True, 148, "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150&h=150&fit=crop&crop=face", "9801000032"),
            ("Bikash Tamang", "Electric Repair", "electrician", "Chitwan", "Chitwan", 27.5312, 84.3523, 4.4, 3, 123, 0.05, 3.0, False, 61, "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face", "9801000033"),
            ("Sunil Karki", "Electric Repair", "electrician", "Tilottama", "Rupandehi", 27.7156, 83.4298, 4.7, 6, 245, 0.02, 2.0, True, 122, "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face", "9801000034"),
            ("Mohan Rai", "Electric Repair", "electrician", "Butwal", "Rupandehi", 27.6998, 83.4512, 4.5, 4, 167, 0.04, 2.5, True, 83, "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face", "9801000035"),
            ("Krishna Oli", "Electric Repair", "electrician", "Bhairahawa", "Rupandehi", 27.5089, 83.4487, 4.6, 5, 198, 0.03, 2.2, True, 99, "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face", "9801000036"),
            ("Anil Thapa", "Electric Repair", "electrician", "Chitwan", "Chitwan", 27.5289, 84.3578, 4.9, 8, 356, 0.01, 1.5, True, 178, "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face", "9801000037"),
            ("Sagar KC", "Electric Repair", "electrician", "Tilottama", "Rupandehi", 27.7201, 83.4334, 4.3, 2, 78, 0.07, 3.2, False, 39, "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=150&h=150&fit=crop&crop=face", "9801000038"),
            ("Ravi Sharma", "Electric Repair", "electrician", "Butwal", "Rupandehi", 27.7034, 83.4456, 4.8, 7, 289, 0.02, 1.8, True, 144, "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=150&h=150&fit=crop&crop=face", "9801000039"),
            ("Dinesh Gurung", "Electric Repair", "electrician", "Bhairahawa", "Rupandehi", 27.5112, 83.4467, 4.4, 3, 134, 0.05, 2.8, True, 67, "https://images.unsplash.com/photo-1590031905470-a1a1feacbb0b?w=150&h=150&fit=crop&crop=face", "9801000040"),
            ("Naresh Pandey", "Electric Repair", "electrician", "Chitwan", "Chitwan", 27.5323, 84.3545, 4.7, 5, 212, 0.03, 2.1, True, 106, "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=150&h=150&fit=crop&crop=face", "9801000041"),
            ("Umesh Rai", "Electric Repair", "electrician", "Tilottama", "Rupandehi", 27.7145, 83.4323, 4.6, 4, 156, 0.04, 2.4, True, 78, "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=150&h=150&fit=crop&crop=face", "9801000042"),
            ("Kamal Joshi", "Electric Repair", "electrician", "Butwal", "Rupandehi", 27.7012, 83.4523, 4.2, 1, 34, 0.09, 4.0, False, 17, "https://images.unsplash.com/photo-1566492031773-4f4e44671d66?w=150&h=150&fit=crop&crop=face", "9801000043"),
            ("Santosh Oli", "Electric Repair", "electrician", "Bhairahawa", "Rupandehi", 27.5095, 83.4534, 4.9, 9, 423, 0.01, 1.2, True, 211, "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?w=150&h=150&fit=crop&crop=face", "9801000044"),
            ("Rajendra Thapa", "Electric Repair", "electrician", "Chitwan", "Chitwan", 27.5267, 84.3589, 4.5, 3, 98, 0.06, 3.1, True, 49, "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=150&h=150&fit=crop&crop=face", "9801000045")
        ]
        
        print(f"📊 Adding {len(providers)} providers...")
        
        # Insert providers
        for i, provider in enumerate(providers, 1):
            cursor.execute("""
                INSERT INTO service_providers 
                (name, service, service_key, location, district, latitude, longitude, rating, experience, 
                 completed_jobs, cancellation_rate, response_time_hours, is_verified, 
                 review_count, image, phone, availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, provider + ('["Mon","Tue","Wed","Thu","Fri","Sat"]',))
            
            if i % 10 == 0:
                print(f"  ✅ Added {i} providers...")
        
        # Get final count
        cursor.execute("SELECT COUNT(*) FROM service_providers")
        final_count = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"🎉 MySQL database setup complete!")
        print(f"📊 Total providers: {final_count}")
        print(f"🏠 Home Cleaning: 15 providers")
        print(f"🔧 Plumbing: 15 providers") 
        print(f"⚡ Electrician: 15 providers")
        print(f"🚀 You can now start your server with: python run_local.py")
        
        return True
        
    except Exception as e:
        print(f"❌ MySQL setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_mysql_interactive()