#!/usr/bin/env python3
"""
Test script to verify AI Insights integration is working properly
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8002"
API_KEY = "development_key_for_testing"

def test_endpoint(endpoint, params=None):
    """Test a specific endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"X-API-Key": API_KEY, "accept": "application/json"}
    
    try:
        print(f"\n=== Testing {endpoint} ===")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: {endpoint}")
            print(f"   Status: {response.status_code}")
            print(f"   Data source: {data.get('data_source', 'unknown')}")
            print(f"   Success: {data.get('success', 'unknown')}")
            return True
        else:
            print(f"❌ FAILED: {endpoint}")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {endpoint}")
        print(f"   Exception: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing AI Insights Integration...")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY}")
    
    test_params = {
        "location": "Building A",
        "time_range": "24h",
        "parameter": "temperature"
    }
    
    tests = [
        ("/insights/climate-analysis", test_params),
        ("/insights/preservation-risk", {"location": "Building A", "time_range": "24h"}),
        ("/insights/recommendations", {"location": "Building A", "time_range": "24h"}),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, params in tests:
        if test_endpoint(endpoint, params):
            passed += 1
    
    print(f"\n=== TEST SUMMARY ===")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! AI Insights integration is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
