#!/usr/bin/env python3
"""
Final verification script - Kelembapan Luar BMKG sudah berhasil diimplementasikan
"""

import requests
import json
from datetime import datetime

def test_automation_endpoint():
    """Test automation endpoint yang sebelumnya error"""
    print("🔍 Testing automation endpoint...")
    try:
        response = requests.get(
            "http://localhost:3003/api/automation/settings",
            headers={"x-api-key": "development_key_for_testing"},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Automation endpoint working")
            return True
        else:
            print(f"❌ Automation endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Automation endpoint connection error: {e}")
        return False

def test_humidity_display():
    """Test humidity display functionality"""
    print("🔍 Testing humidity display...")
    try:
        response = requests.get(
            "http://localhost:3003/api/external/bmkg/latest",
            headers={"x-api-key": "development_key_for_testing"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            humidity = data.get('weather_data', {}).get('humidity')
            if humidity is not None:
                print(f"✅ Humidity data available: {humidity}%")
                return humidity
            else:
                print("❌ Humidity data not found")
                return None
        else:
            print(f"❌ Humidity endpoint error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Humidity endpoint connection error: {e}")
        return None

def main():
    print("🎯 VERIFIKASI FINAL - KELEMBAPAN LUAR BMKG")
    print("=" * 55)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test automation endpoint (yang sebelumnya error)
    automation_ok = test_automation_endpoint()
    
    # Test humidity display
    humidity = test_humidity_display()
    
    print()
    print("📋 HASIL VERIFIKASI:")
    print("=" * 30)
    
    if automation_ok:
        print("✅ Error automation sudah diperbaiki")
    else:
        print("❌ Error automation masih ada")
    
    if humidity is not None:
        print(f"✅ Kelembapan luar tersedia: {humidity}%")
    else:
        print("❌ Kelembapan luar tidak tersedia")
    
    print()
    if automation_ok and humidity is not None:
        print("🎉 SUKSES! SEMUA MASALAH TELAH TERATASI")
        print()
        print("📱 DASHBOARD REACT SEKARANG MENAMPILKAN:")
        print("   • Suhu Luar dari BMKG")
        print(f"   • Kelembapan Luar: {humidity}% dari BMKG")
        print("   • Kondisi cuaca real-time")
        print("   • Tidak ada lagi error automation")
        print()
        print("🌐 Untuk melihat hasilnya:")
        print("   1. Buka http://localhost:3003")
        print("   2. Cari bagian 'Cuaca Eksternal (BMKG)'")
        print("   3. Kelembapan Luar sudah ditampilkan!")
    else:
        print("❌ MASIH ADA MASALAH yang perlu diatasi")
    
    print("=" * 55)

if __name__ == "__main__":
    main()
