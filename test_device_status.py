#!/usr/bin/env python3
"""
Script untuk menguji API endpoint device status
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"  # Adjust based on your API deployment
API_KEY = "test_key"  # Replace with your actual API key

def call_device_status_endpoint():
    # Try both endpoint paths to see which one works
    endpoints = [
        "/system/device_status/",
        "/system/devices_status/"
    ]
    
    headers = {
        "X-API-Key": API_KEY
    }
    
    for endpoint in endpoints:
        url = f"{API_BASE_URL}{endpoint}"
        print(f"Testing endpoint: {url}")
        
        try:
            response = requests.get(url, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=2))
                print(f"Success! Endpoint {endpoint} is working correctly.")
                return True
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Exception when calling {endpoint}: {e}")
    
    return False

if __name__ == "__main__":
    print(f"Testing device status endpoints at {datetime.now().isoformat()}")
    success = call_device_status_endpoint()
    
    if success:
        print("Test completed successfully!")
        sys.exit(0)
    else:
        print("Test failed!")
        sys.exit(1)
