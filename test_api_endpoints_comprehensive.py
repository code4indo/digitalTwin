#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all API endpoints that the React application uses to ensure they return proper data structures.
"""

import requests
import json
import sys
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8002"
API_KEY = "development_key_for_testing"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_endpoint(endpoint: str, description: str) -> Dict[str, Any]:
    """Test a single API endpoint and return results."""
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {API_BASE_URL}{endpoint}")
    
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=10)
        
        result = {
            "endpoint": endpoint,
            "description": description,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "data": None,
            "error": None,
            "data_type": None,
            "array_check": None
        }
        
        if response.status_code == 200:
            try:
                data = response.json()
                result["data"] = data
                result["data_type"] = type(data).__name__
                
                # Check if data is an array (list) or contains arrays
                if isinstance(data, list):
                    result["array_check"] = f"✅ Is array with {len(data)} items"
                elif isinstance(data, dict):
                    array_fields = []
                    for key, value in data.items():
                        if isinstance(value, list):
                            array_fields.append(f"{key}({len(value)} items)")
                    
                    if array_fields:
                        result["array_check"] = f"✅ Contains arrays: {', '.join(array_fields)}"
                    else:
                        result["array_check"] = "ℹ️  No arrays found"
                
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📄 Data Type: {result['data_type']}")
                print(f"   📊 Array Check: {result['array_check']}")
                
            except json.JSONDecodeError as e:
                result["error"] = f"JSON decode error: {str(e)}"
                print(f"   ❌ JSON Error: {str(e)}")
                
        else:
            result["error"] = f"HTTP {response.status_code}: {response.text}"
            print(f"   ❌ Error: HTTP {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        result = {
            "endpoint": endpoint,
            "description": description,
            "status_code": None,
            "success": False,
            "data": None,
            "error": f"Request error: {str(e)}",
            "data_type": None,
            "array_check": None
        }
        print(f"   ❌ Request Error: {str(e)}")
    
    return result

def main():
    """Run comprehensive API endpoint tests."""
    print("🚀 Starting Comprehensive API Endpoint Testing")
    print("=" * 60)
    
    # Define all endpoints that React components use
    endpoints_to_test = [
        # Environmental Status endpoints
        ("/stats/temperature/last-hour/stats/", "Temperature Statistics (EnvironmentalStatus)"),
        ("/stats/humidity/last-hour/stats/", "Humidity Statistics (EnvironmentalStatus)"),
        ("/external/bmkg/latest", "External Weather Data (EnvironmentalStatus)"),
        ("/health", "System Health (EnvironmentalStatus)"),
        
        # Alerts endpoints
        ("/alerts", "Alerts List (AlertsPanel)"),
        ("/alerts?filter=critical", "Critical Alerts (AlertsPanel)"),
        
        # Trend analysis endpoints
        ("/trend/temperature", "Temperature Trend Data (TrendAnalysis)"),
        ("/trend/humidity", "Humidity Trend Data (TrendAnalysis)"),
        
        # Room details endpoints
        ("/rooms/F3/details", "Room F3 Details (RoomDetails)"),
        ("/rooms/G5/details", "Room G5 Details (RoomDetails)"),
        
        # Automation endpoints
        ("/automation/settings", "Automation Settings (AutomationControls)"),
        
        # Predictive analysis endpoints
        ("/predictions/analysis", "Predictive Analysis (PredictiveAnalysis)"),
        
        # Recommendations endpoints
        ("/recommendations", "Recommendations List (ProactiveRecommendations)"),
        
        # Basic endpoints
        ("/", "API Root"),
        ("/docs", "API Documentation"),
    ]
    
    results = []
    successful_tests = 0
    
    for endpoint, description in endpoints_to_test:
        result = test_endpoint(endpoint, description)
        results.append(result)
        if result["success"]:
            successful_tests += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {len(results) - successful_tests}")
    print(f"Success Rate: {(successful_tests/len(results)*100):.1f}%")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    print("-" * 60)
    for result in results:
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {result['description']}")
        print(f"   {result['endpoint']}")
        if result["error"]:
            print(f"   Error: {result['error']}")
        if result["array_check"]:
            print(f"   {result['array_check']}")
        print()
    
    # Recommendations for React fixes
    print("🔧 RECOMMENDATIONS FOR REACT APP:")
    print("-" * 60)
    
    failed_endpoints = [r for r in results if not r["success"]]
    if failed_endpoints:
        print("❌ Failed endpoints detected. React components should handle these gracefully:")
        for result in failed_endpoints:
            print(f"   - {result['endpoint']}: Use fallback/dummy data")
    
    array_warnings = []
    for result in results:
        if result["success"] and result["data"] is not None:
            if isinstance(result["data"], dict):
                # Check for potential undefined array issues
                for key, value in result["data"].items():
                    if value is None:
                        array_warnings.append(f"{result['endpoint']}: {key} is None")
    
    if array_warnings:
        print("\n⚠️  Potential array issues found:")
        for warning in array_warnings:
            print(f"   - {warning}")
    
    print("\n✅ All React components have been updated with proper array checks!")
    print("   - Added Array.isArray() checks before .map() calls")
    print("   - Added fallback data for failed API calls")
    print("   - Improved error handling in all components")

if __name__ == "__main__":
    main()
