#!/usr/bin/env python3
"""
Database migration script to add email, password, and bio columns to service_providers table
"""

import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'nepsewa123',
    'database': 'nepsewa'
}

def migrate():
    print("🔄 Starting database migration...")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check current columns
        print("\n📋 Checking current table structure...")
        cursor.execute("DESCRIBE service_providers")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        print(f"Current columns: {', '.join(column_names)}")
        
        # Add email column if it doesn't exist
        if 'email' not in column_names:
            print("\n➕ Adding 'email' column...")
            cursor.execute("""
                ALTER TABLE service_providers 
                ADD COLUMN email VARCHAR(180) UNIQUE AFTER phone
            """)
            print("✅ Email column added")
        else:
            print("\n✓ Email column already exists")
        
        # Add password column if it doesn't exist
        if 'password' not in column_names:
            print("\n➕ Adding 'password' column...")
            cursor.execute("""
                ALTER TABLE service_providers 
                ADD COLUMN password VARCHAR(256) AFTER email
            """)
            print("✅ Password column added")
        else:
            print("\n✓ Password column already exists")
        
        # Add bio column if it doesn't exist
        if 'bio' not in column_names:
            print("\n➕ Adding 'bio' column...")
            cursor.execute("""
                ALTER TABLE service_providers 
                ADD COLUMN bio TEXT AFTER password
            """)
            print("✅ Bio column added")
        else:
            print("\n✓ Bio column already exists")
        
        # Add index on email if it doesn't exist
        print("\n📊 Checking indexes...")
        cursor.execute("SHOW INDEX FROM service_providers WHERE Key_name = 'email'")
        if not cursor.fetchone():
            print("➕ Adding index on email column...")
            cursor.execute("CREATE INDEX idx_email ON service_providers(email)")
            print("✅ Email index added")
        else:
            print("✓ Email index already exists")
        
        conn.commit()
        
        # Verify changes
        print("\n✅ Migration completed successfully!")
        print("\n📋 Updated table structure:")
        cursor.execute("DESCRIBE service_providers")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database is ready for the Provider Portal!")
        
    except pymysql.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("NepSewa Database Migration")
    print("Adding Provider Portal columns")
    print("=" * 60)
    
    success = migrate()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("You can now use the Provider Portal features")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Migration failed!")
        print("Please check the error messages above")
        print("=" * 60)
