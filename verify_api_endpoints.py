#!/usr/bin/env python3
"""
Simple HTTP verification script for API endpoints
"""
import requests
import sys
import json
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8002"  # From docker-compose.yml
API_KEY = "development_key_for_testing"  # Default from docker-compose.yml
TIMEOUT = 5  # seconds

# Headers for authentication
headers = {
    "X-API-Key": API_KEY
}

def check_endpoint(endpoint, description):
    """Test a specific endpoint and print results"""
    url = f"{API_BASE_URL}{endpoint}"
    print(f"\n==== Testing {description} ====")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        status_code = response.status_code
        
        if status_code == 200:
            print(f"✅ Success (Status: {status_code})")
            try:
                data = response.json()
                print("Response data:")
                print(json.dumps(data, indent=2))
                return True
            except json.JSONDecodeError:
                print("⚠️ Warning: Response is not valid JSON")
                print(f"Raw response: {response.text[:200]}")
                return False
        else:
            print(f"❌ Failed (Status: {status_code})")
            print(f"Response: {response.text[:200]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {type(e).__name__} - {str(e)}")
        return False

def main():
    """Main function to test all endpoints"""
    print("=" * 70)
    print("API ENDPOINT VERIFICATION")
    print("=" * 70)
    print(f"Base URL: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Test health endpoint first
    print("\nTesting API health...")
    health_ok = check_endpoint("/system/health/", "Health Endpoint")
    
    if not health_ok:
        print("\n⚠️ Health check failed. API might be down or inaccessible.")
        print("Further tests may fail. Check if the API server is running.")
    
    # Check temperature stats
    temp_ok = check_endpoint("/stats/temperature/", "Temperature Statistics Endpoint")
    
    # Check humidity stats
    hum_ok = check_endpoint("/stats/humidity/", "Humidity Statistics Endpoint")
    
    # Check environmental stats
    env_ok = check_endpoint("/stats/environmental/", "Environmental Statistics Endpoint")
    
    # Test with filter
    print("\nTesting with filter parameters...")
    start_time = (datetime.now() - timedelta(hours=1)).isoformat()
    filter_ok = check_endpoint(f"/stats/environmental/?start_time={start_time}", "Filtered Environmental Stats (last hour)")
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"Health endpoint:            {'✅ OK' if health_ok else '❌ FAILED'}")
    print(f"Temperature stats endpoint: {'✅ OK' if temp_ok else '❌ FAILED'}")
    print(f"Humidity stats endpoint:    {'✅ OK' if hum_ok else '❌ FAILED'}")
    print(f"Environmental stats:        {'✅ OK' if env_ok else '❌ FAILED'}")
    print(f"Filtered request:           {'✅ OK' if filter_ok else '❌ FAILED'}")
    print("=" * 70)
    
    if all([health_ok, temp_ok, hum_ok, env_ok, filter_ok]):
        print("\n✅ ALL TESTS PASSED: The API endpoints are working correctly.")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED: There may be issues with the API endpoints.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
