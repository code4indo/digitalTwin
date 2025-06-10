#!/usr/bin/env python3
"""
Script untuk memverifikasi bahwa frontend React sudah menggunakan 
sistem rekomendasi yang ditingkatkan
"""

import requests
import time
from datetime import datetime

def test_frontend_recommendations():
    """Test apakah frontend bisa mengakses rekomendasi baru"""
    print("="*60)
    print("🔍 TESTING FRONTEND INTEGRATION")
    print("="*60)
    
    # Test akses frontend
    try:
        print("1. Testing frontend accessibility...")
        frontend_response = requests.get("http://localhost:3003", timeout=10)
        if frontend_response.status_code == 200:
            print("✅ Frontend accessible on port 3003")
        else:
            print(f"❌ Frontend not accessible: {frontend_response.status_code}")
    except Exception as e:
        print(f"❌ Frontend connection error: {e}")
    
    # Test API rekomendasi langsung
    try:
        print("\n2. Testing API recommendations directly...")
        api_headers = {"X-API-Key": "development_key_for_testing"}
        api_response = requests.get("http://localhost:8002/recommendations/proactive", 
                                  headers=api_headers, timeout=10)
        
        if api_response.status_code == 200:
            data = api_response.json()
            total_recs = data.get('total_recommendations', 0)
            priority_recs = len(data.get('priority_recommendations', []))
            building_insights = len(data.get('building_insights', []))
            
            print(f"✅ API working: {total_recs} total recommendations")
            print(f"   - Priority recommendations: {priority_recs}")
            print(f"   - Building insights: {building_insights}")
            
            # Show sample recommendations
            print("\n📋 Sample Recommendations:")
            for i, rec in enumerate(data.get('priority_recommendations', [])[:3], 1):
                print(f"   {i}. {rec.get('title', 'N/A')} (Priority: {rec.get('priority', 'N/A')})")
                if rec.get('room'):
                    print(f"      Room: {rec.get('room')}")
                if rec.get('specific_actions'):
                    print(f"      Actions: {len(rec.get('specific_actions'))} steps")
                print()
                
        else:
            print(f"❌ API error: {api_response.status_code}")
            print(f"Response: {api_response.text}")
    except Exception as e:
        print(f"❌ API connection error: {e}")

def test_containers_status():
    """Test status semua container"""
    print("\n" + "="*60)
    print("📦 CONTAINER STATUS CHECK")
    print("="*60)
    
    import subprocess
    
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        containers = {
            'api_service': False,
            'web_react_service': False,
            'influxdb_service': False,
            'grafana_service': False
        }
        
        for line in lines:
            for container in containers.keys():
                if container in line and 'Up' in line:
                    containers[container] = True
                    
        print("Container Status:")
        for container, status in containers.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {container}: {'Running' if status else 'Not Running'}")
            
    except Exception as e:
        print(f"❌ Error checking containers: {e}")

def main():
    """Main verification function"""
    print("🔧 VERIFIKASI INTEGRASI FRONTEND & BACKEND")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_containers_status()
    test_frontend_recommendations()
    
    print("\n" + "="*60)
    print("📝 INSTRUKSI TESTING MANUAL")
    print("="*60)
    print("1. Buka browser dan akses: http://localhost:3003")
    print("2. Navigasi ke section 'Peringatan & Rekomendasi'")
    print("3. Pastikan terlihat:")
    print("   ✅ Multiple recommendations (bukan hanya 2)")
    print("   ✅ Priority badges (CRITICAL, HIGH, MEDIUM)")
    print("   ✅ Room-specific recommendations")
    print("   ✅ Detailed specific actions untuk setiap recommendation")
    print("   ✅ Preservation risk dan energy impact analysis")
    print("\n4. Jika masih tampil data lama:")
    print("   - Refresh browser (Ctrl+F5)")
    print("   - Clear browser cache")
    print("   - Check browser console untuk error")
    
    print(f"\n🎯 Expected: {8} recommendations total")
    print("📊 Expected: Building performance insights")
    print("🏠 Expected: Room-specific analysis (G4, F3, G2, G3)")

if __name__ == "__main__":
    main()
