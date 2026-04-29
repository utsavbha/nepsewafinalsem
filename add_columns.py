#!/usr/bin/env python3
"""
Simple script to add email, password, and bio columns to service_providers table
Run this manually: python3 add_columns.py
"""

import pymysql

try:
    # Connect to database
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='nepsewa123',
        database='nepsewa'
    )
    
    cursor = conn.cursor()
    
    print("Adding columns to service_providers table...")
    
    # Add email column
    try:
        cursor.execute("ALTER TABLE service_providers ADD COLUMN email VARCHAR(180) UNIQUE")
        print("✅ Added email column")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("✓ Email column already exists")
        else:
            print(f"❌ Error adding email column: {e}")
    
    # Add password column
    try:
        cursor.execute("ALTER TABLE service_providers ADD COLUMN password VARCHAR(256)")
        print("✅ Added password column")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("✓ Password column already exists")
        else:
            print(f"❌ Error adding password column: {e}")
    
    # Add bio column
    try:
        cursor.execute("ALTER TABLE service_providers ADD COLUMN bio TEXT")
        print("✅ Added bio column")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("✓ Bio column already exists")
        else:
            print(f"❌ Error adding bio column: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n🎉 Database updated successfully!")
    print("You can now use the Provider Portal features.")
    
except Exception as e:
    print(f"❌ Database connection error: {e}")
    print("Make sure MySQL is running and credentials are correct.")