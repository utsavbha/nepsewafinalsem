#!/usr/bin/env python3
"""
Quick test to verify all fixes are working
"""

import subprocess
import time
import requests
import threading
import sys

def start_server():
    """Start the Flask server"""
    try:
        subprocess.run([sys.executable, "render_start.py"], cwd=".")
    except KeyboardInterrupt:
        pass

def test_endpoints():
    """Test key endpoints"""
    time.sleep(3)  # Wait for server to start
    
    base_url = "http://127.0.0.1:8001"
    
    tests = [
        ("Health Check", f"{base_url}/health"),
        ("Status Check", f"{base_url}/api/status"),
        ("Home Page", f"{base_url}/"),
        ("Services Page", f"{base_url}/services"),
        ("Top Professionals", f"{base_url}/api/top-professionals"),
        ("Services API", f"{base_url}/api/services"),
        ("Providers API", f"{base_url}/api/providers")
    ]
    
    print("🧪 Testing NepSewa endpoints...")
    
    for name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            print(f"{status} {name}")
            
            if response.status_code == 200 and 'api' in url:
                try:
                    data = response.json()
                    if 'success' in data:
                        print(f"    Success: {data['success']}")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    print("🚀 Starting NepSewa test...")
    
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Run tests
    test_endpoints()