#!/usr/bin/env python3
"""
Test script to verify NepSewa deployment
"""

import requests
import json

def test_deployment(base_url="https://nepsewa-app.onrender.com"):
    """Test the deployed NepSewa application"""
    
    print(f"🧪 Testing NepSewa deployment at: {base_url}")
    
    tests = [
        {
            "name": "Health Check",
            "url": f"{base_url}/health",
            "method": "GET"
        },
        {
            "name": "Home Page",
            "url": f"{base_url}/",
            "method": "GET"
        },
        {
            "name": "Services Page",
            "url": f"{base_url}/services",
            "method": "GET"
        },
        {
            "name": "Top Professionals API",
            "url": f"{base_url}/api/top-professionals",
            "method": "GET"
        },
        {
            "name": "Services API",
            "url": f"{base_url}/api/services",
            "method": "GET"
        },
        {
            "name": "Providers API",
            "url": f"{base_url}/api/providers",
            "method": "GET"
        },
        {
            "name": "Populate Database",
            "url": f"{base_url}/api/populate-db",
            "method": "POST"
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            print(f"\n🔍 Testing: {test['name']}")
            
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=30)
            else:
                response = requests.post(test['url'], timeout=30)
            
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"   Status: {status}")
            
            # Try to parse JSON response
            try:
                data = response.json()
                if 'success' in data:
                    print(f"   Success: {data['success']}")
                if 'message' in data:
                    print(f"   Message: {data['message']}")
            except:
                print(f"   Response length: {len(response.text)} chars")
            
            results.append({
                "test": test['name'],
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append({
                "test": test['name'],
                "status_code": 0,
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print(f"\n📊 Test Summary:")
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Deployment is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the deployment.")
    
    return results

if __name__ == "__main__":
    test_deployment()