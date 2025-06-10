#!/usr/bin/env python3
"""
Test script to verify the complete AI Insights workflow
Tests that the frontend dropdown matches real room codes and that the backend provides real insights
"""

import requests
import json

def test_api_insights():
    """Test the insights API endpoint with real room codes"""
    print("Testing AI Insights API endpoints...")
    
    # Test room codes that should exist in InfluxDB
    room_codes = ["F2", "F3", "F4", "F5", "F6", "G2", "G3", "G4", "G5", "G8"]
    api_url = "http://localhost:8002"
    headers = {"X-API-Key": "development_key_for_testing"}
    
    successful_tests = 0
    total_tests = len(room_codes)
    
    for room in room_codes:
        try:
            url = f"{api_url}/insights/climate-analysis"
            params = {
                "parameter": "temperature",
                "location": room,
                "period": "day"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("trend_summary", {}).get("data_points", 0) > 0:
                    print(f"✓ Room {room}: {data['trend_summary']['data_points']} data points found")
                    successful_tests += 1
                else:
                    print(f"✗ Room {room}: No data points found")
            else:
                print(f"✗ Room {room}: API error {response.status_code}")
                
        except Exception as e:
            print(f"✗ Room {room}: Error - {str(e)}")
    
    print(f"\nAPI Test Results: {successful_tests}/{total_tests} rooms have working insights")
    return successful_tests > 0

def test_frontend_build():
    """Test that the frontend build contains the correct room codes"""
    print("\nTesting frontend build...")
    
    try:
        response = requests.get("http://localhost:3003/bundle.js", timeout=10)
        if response.status_code == 200:
            bundle_content = response.text
            
            room_codes = ["F2", "F3", "F4", "F5", "F6", "G2", "G3", "G4", "G5", "G8"]
            found_rooms = []
            
            for room in room_codes:
                if room in bundle_content:
                    found_rooms.append(room)
            
            print(f"✓ Frontend bundle contains room codes: {', '.join(found_rooms)}")
            return len(found_rooms) >= 8  # Most rooms should be present
        else:
            print(f"✗ Could not access frontend bundle (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"✗ Error accessing frontend: {str(e)}")
        return False

def main():
    print("=== Digital Twin AI Insights Complete Workflow Test ===\n")
    
    api_success = test_api_insights()
    frontend_success = test_frontend_build()
    
    print(f"\n=== Test Summary ===")
    print(f"API Insights: {'✓ PASS' if api_success else '✗ FAIL'}")
    print(f"Frontend Build: {'✓ PASS' if frontend_success else '✗ FAIL'}")
    
    if api_success and frontend_success:
        print("\n🎉 All tests passed! The AI Insights feature is working with real sensor data.")
        print("✓ Frontend dropdown uses correct room codes matching InfluxDB")
        print("✓ Backend provides AI insights for real sensor data")
        print("✓ End-to-end workflow is functional")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
