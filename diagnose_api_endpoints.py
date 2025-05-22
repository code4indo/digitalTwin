#!/usr/bin/env python3
"""
Diagnose issues with API endpoints
"""
import requests
import sys
import os

API_BASE_URL = "http://localhost:8002"
API_KEY = "development_key_for_testing"

headers = {
    "X-API-Key": API_KEY
}

def check_api_connectivity():
    """Check if we can connect to the API at all"""
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API is accessible at /docs")
            return True
        else:
            print(f"❌ API /docs returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        return False

def check_api_endpoints():
    """List the available endpoints from the OpenAPI schema"""
    try:
        response = requests.get(f"{API_BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\nAvailable endpoints:")
            paths = data.get("paths", {})
            for path in sorted(paths.keys()):
                methods = ", ".join(paths[path].keys()).upper()
                print(f"  {path} [{methods}]")
            
            # Check specifically for our stats endpoints
            stats_endpoints = [p for p in paths.keys() if p.startswith("/stats/")]
            if stats_endpoints:
                print("\n✅ Stats endpoints found:")
                for endpoint in stats_endpoints:
                    print(f"  {endpoint}")
            else:
                print("\n❌ No /stats/* endpoints found in the API schema")
            
            return True
        else:
            print(f"❌ Cannot retrieve OpenAPI schema: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking endpoints: {str(e)}")
        return False

def check_specific_endpoint(endpoint):
    """Try to access a specific endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    print(f"\nTesting endpoint: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        if response.status_code == 200:
            try:
                data = response.json()
                print("Response body:")
                print(data)
            except:
                print("Response body (non-JSON):")
                print(response.text[:500])  # Print first 500 chars
        else:
            print("Error response:")
            print(response.text)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return None

def main():
    print("=== API Endpoint Diagnostic ===")
    
    if not check_api_connectivity():
        print("\n❌ Cannot connect to API server. Please check if it's running.")
        return 1
    
    check_api_endpoints()
    
    # Check the endpoint we're having trouble with
    status_code = check_specific_endpoint("/stats/temperature/")
    
    # Check another known good endpoint for comparison
    print("\n=== Checking a known endpoint for comparison ===")
    check_specific_endpoint("/system/health/")
    
    # Provide troubleshooting advice
    print("\n=== Diagnostic Summary ===")
    
    if status_code == 404:
        print("""
The /stats/temperature/ endpoint returns 404 Not Found. Possible causes:
1. The API server hasn't loaded the updated code with the new endpoints
2. The endpoint path is different than expected
3. There's an issue with how the endpoint was registered in FastAPI

Recommended actions:
1. Make sure the API container has the updated code
2. Restart the API container: docker restart api_service
3. Check the API logs for any errors: docker logs api_service
4. Verify the endpoint path is correctly implemented in the code
""")
    
    print("\nFor more information, check the API server logs.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
