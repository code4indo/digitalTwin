#!/usr/bin/env python3
"""
Comprehensive Test untuk Verifikasi API Key Gemini berfungsi dengan baik
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8002"
API_KEY = "development_key_for_testing"

# Headers untuk semua request
headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def test_endpoint(url, endpoint_name):
    """Test single endpoint dan verifikasi response"""
    print(f"\n🔍 Testing {endpoint_name}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check basic response structure
            if data.get('success', False):
                print(f"   ✅ SUCCESS: Response successful")
                
                # Check for AI source indication
                data_source = data.get('data_source', 'unknown')
                print(f"   📊 Data Source: {data_source}")
                
                # Check for AI-specific indicators
                confidence = data.get('ai_confidence', data.get('confidence', 'unknown'))
                print(f"   🎯 Confidence Level: {confidence}")
                
                # Check if we have insights content
                insights = data.get('insights', {})
                if insights:
                    print(f"   💡 Insights Available: Yes")
                    
                    # Check for key insight fields
                    key_fields = ['ringkasan_kondisi', 'rekomendasi_aksi', 'tren_prediksi']
                    for field in key_fields:
                        if field in insights:
                            content = insights[field]
                            if isinstance(content, str) and len(content) > 50:
                                print(f"   📝 {field}: Rich content detected ({len(content)} chars)")
                            elif isinstance(content, list) and len(content) > 0:
                                print(f"   📝 {field}: {len(content)} items")
                
                # Check if using real Gemini AI vs fallback
                if data_source == "gemini_ai":
                    print(f"   🤖 GEMINI AI: ACTIVE ✅")
                    return True, "gemini_ai"
                elif data_source == "rule_based_fallback":
                    print(f"   ⚠️  FALLBACK: Using rule-based system")
                    return True, "fallback"
                else:
                    print(f"   ❓ UNKNOWN: Data source unclear")
                    return True, "unknown"
                    
            else:
                print(f"   ❌ FAILED: Response not successful")
                print(f"   📄 Response: {data}")
                return False, "error"
                
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📄 Error: {error_data}")
            except:
                print(f"   📄 Raw Response: {response.text}")
            return False, "http_error"
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ TIMEOUT: Request took too long")
        return False, "timeout"
    except requests.exceptions.RequestException as e:
        print(f"   💥 REQUEST ERROR: {str(e)}")
        return False, "request_error"
    except Exception as e:
        print(f"   🔥 UNEXPECTED ERROR: {str(e)}")
        return False, "unexpected_error"

def main():
    print("🚀 COMPREHENSIVE GEMINI API VERIFICATION")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY}")
    
    # Test cases
    test_cases = [
        {
            "name": "Climate Analysis - Temperature Day",
            "url": f"{API_BASE_URL}/insights/climate-analysis?parameter=temperature&period=day&location=all"
        },
        {
            "name": "Climate Analysis - Humidity Week", 
            "url": f"{API_BASE_URL}/insights/climate-analysis?parameter=humidity&period=week&location=all"
        },
        {
            "name": "Preservation Risk - Temperature",
            "url": f"{API_BASE_URL}/insights/preservation-risk?parameter=temperature&period=month&location=archive"
        },
        {
            "name": "Preservation Risk - Humidity",
            "url": f"{API_BASE_URL}/insights/preservation-risk?parameter=humidity&period=week&location=all"
        },
        {
            "name": "Recommendations - Optimal Condition",
            "url": f"{API_BASE_URL}/insights/recommendations?parameter=temperature&condition=optimal"
        },
        {
            "name": "Recommendations - High Risk",
            "url": f"{API_BASE_URL}/insights/recommendations?parameter=humidity&condition=high"
        }
    ]
    
    # Run tests
    results = []
    gemini_count = 0
    fallback_count = 0
    error_count = 0
    
    for test_case in test_cases:
        success, source_type = test_endpoint(test_case["url"], test_case["name"])
        results.append({
            "name": test_case["name"],
            "success": success,
            "source_type": source_type
        })
        
        if source_type == "gemini_ai":
            gemini_count += 1
        elif source_type == "fallback":
            fallback_count += 1
        else:
            error_count += 1
            
        # Small delay between requests
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print()
    print(f"🤖 Gemini AI Active: {gemini_count}")
    print(f"⚠️  Fallback Used: {fallback_count}")
    print(f"❌ Errors: {error_count}")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        source_icon = {"gemini_ai": "🤖", "fallback": "⚠️", "unknown": "❓"}.get(result["source_type"], "❌")
        print(f"   {status} {source_icon} {result['name']} ({result['source_type']})")
    
    # Final verdict
    print("\n" + "=" * 50)
    if gemini_count > 0:
        print("🎉 VERDICT: GEMINI API KEY IS WORKING! 🎉")
        print(f"   {gemini_count} endpoint(s) successfully using Gemini AI")
        if fallback_count > 0:
            print(f"   Note: {fallback_count} endpoint(s) still using fallback (normal for some endpoints)")
    elif fallback_count > 0:
        print("⚠️  VERDICT: API KEY MIGHT NOT BE WORKING")
        print("   All endpoints using fallback system")
        print("   Check GEMINI_API_KEY environment variable")
    else:
        print("❌ VERDICT: SYSTEM NOT WORKING")
        print("   Multiple errors detected")
    print("=" * 50)

if __name__ == "__main__":
    main()
