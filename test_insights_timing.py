#!/usr/bin/env python3

import requests
import time
import sys

def test_insights_api():
    """Test insights API endpoints with timing"""
    
    base_url = "http://localhost:8002"
    api_key = "development_key_for_testing"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    endpoints = [
        ("climate-analysis", "Climate Insights"),
        ("recommendations", "Recommendations"), 
        ("preservation-risk", "Preservation Risk")
    ]
    
    print("Testing Insights API Endpoints")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key}")
    print(f"Timeout: 30 seconds")
    print()
    
    for endpoint, name in endpoints:
        url = f"{base_url}/insights/{endpoint}"
        print(f"Testing {name}...")
        print(f"URL: {url}")
        
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=30)
            end_time = time.time()
            
            duration = end_time - start_time
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: {duration:.2f}s")
                data = response.text
                if len(data) > 300:
                    print(f"Response (first 300 chars): {data[:300]}...")
                else:
                    print(f"Response: {data}")
            else:
                print(f"❌ ERROR: Status {response.status_code} after {duration:.2f}s")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: Request exceeded 30 seconds")
        except requests.exceptions.RequestException as e:
            print(f"❌ REQUEST ERROR: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
            
        print("-" * 40)
        print()

if __name__ == "__main__":
    test_insights_api()
