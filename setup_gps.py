#!/usr/bin/env python3
"""
Setup script to add GPS coordinates to existing providers
Run this once to populate latitude/longitude for all providers
"""

import pymysql
import random

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root", 
    "password": "nepsewa123",
    "database": "nepsewa",
    "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

def add_gps_coordinates():
    """Add realistic GPS coordinates to all providers"""
    
    # Define precise coordinates for each location with realistic spread
    location_coordinates = {
        'Butwal': {
            'center': {'lat': 27.7000, 'lng': 83.4500},
            'spread': 0.02,  # ~2km spread
            'description': 'Butwal Municipality'
        },
        'Tilottama': {
            'center': {'lat': 27.7200, 'lng': 83.4300}, 
            'spread': 0.015,  # ~1.5km spread
            'description': 'Tilottama Municipality'
        },
        'Bhairahawa': {
            'center': {'lat': 27.5081, 'lng': 83.4519},
            'spread': 0.025,  # ~2.5km spread
            'description': 'Bhairahawa (Siddharthanagar)'
        },
        'Chitwan': {
            'center': {'lat': 27.5291, 'lng': 84.3542},
            'spread': 0.03,  # ~3km spread
            'description': 'Chitwan District'
        }
    }
    
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # First, check if latitude/longitude columns exist
            cur.execute("SHOW COLUMNS FROM service_providers LIKE 'latitude'")
            if not cur.fetchone():
                print("Adding latitude column...")
                cur.execute("ALTER TABLE service_providers ADD COLUMN latitude DECIMAL(10,8) DEFAULT NULL")
            
            cur.execute("SHOW COLUMNS FROM service_providers LIKE 'longitude'")  
            if not cur.fetchone():
                print("Adding longitude column...")
                cur.execute("ALTER TABLE service_providers ADD COLUMN longitude DECIMAL(11,8) DEFAULT NULL")
            
            # Get all providers
            cur.execute("SELECT id, name, location FROM service_providers")
            providers = cur.fetchall()
            
            print(f"Found {len(providers)} providers to update")
            
            updated_count = 0
            location_stats = {}
            
            for provider in providers:
                location = provider['location']
                
                if location not in location_coordinates:
                    print(f"Warning: Unknown location '{location}' for provider {provider['name']}")
                    continue
                
                coords = location_coordinates[location]
                
                # Generate random coordinates within the location area
                lat_offset = (random.random() - 0.5) * coords['spread']
                lng_offset = (random.random() - 0.5) * coords['spread']
                
                provider_lat = coords['center']['lat'] + lat_offset
                provider_lng = coords['center']['lng'] + lng_offset
                
                # Update provider with GPS coordinates
                cur.execute("""
                    UPDATE service_providers 
                    SET latitude = %s, longitude = %s 
                    WHERE id = %s
                """, (provider_lat, provider_lng, provider['id']))
                
                updated_count += 1
                
                # Track stats by location
                if location not in location_stats:
                    location_stats[location] = 0
                location_stats[location] += 1
                
                print(f"✓ Updated {provider['name']} in {location}: {provider_lat:.6f}, {provider_lng:.6f}")
        
        conn.commit()
        
        print(f"\n🎉 Successfully updated {updated_count} providers with GPS coordinates!")
        print("\nLocation breakdown:")
        for location, count in location_stats.items():
            desc = location_coordinates[location]['description']
            print(f"  {location} ({desc}): {count} providers")
        
        # Verify the update
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM service_providers WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
            result = cur.fetchone()
            print(f"\nVerification: {result['total']} providers now have GPS coordinates")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def test_nearby_query():
    """Test the nearby providers query"""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # Test query from Butwal center
            test_lat, test_lng = 27.7000, 83.4500
            radius = 10
            
            query = """
                SELECT name, location, latitude, longitude,
                (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * 
                cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * 
                sin(radians(latitude)))) AS distance_km
                FROM service_providers 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                HAVING distance_km <= %s 
                ORDER BY distance_km ASC 
                LIMIT 10
            """
            
            cur.execute(query, [test_lat, test_lng, test_lat, radius])
            results = cur.fetchall()
            
            print(f"\n🧪 Test Query Results (within {radius}km of Butwal center):")
            for provider in results:
                print(f"  {provider['name']} ({provider['location']}): {provider['distance_km']:.2f}km")
            
            if not results:
                print("  No providers found - this indicates an issue!")
            
    except Exception as e:
        print(f"❌ Test query error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🗺️  NepSewa GPS Coordinates Setup")
    print("=" * 40)
    
    if add_gps_coordinates():
        test_nearby_query()
        print("\n✅ Setup complete! You can now use the nearby providers feature.")
        print("💡 Visit http://localhost:8000/nearby to test the location-based search")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")