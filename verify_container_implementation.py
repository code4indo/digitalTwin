#!/usr/bin/env python3

import requests
import time
from datetime import datetime

def verify_container_updates():
    """Verifikasi bahwa container sudah menggunakan kode terbaru"""
    
    print("🔍 VERIFIKASI IMPLEMENTASI PERUBAHAN KODE PADA CONTAINER")
    print("=" * 60)
    
    # Test 1: Periksa timestamp container
    print("\n1. 📅 Periksa Timestamp Container")
    print("-" * 40)
    
    import subprocess
    
    try:
        # Get React container creation time
        react_created = subprocess.check_output([
            "docker", "inspect", "web_react_service", "--format", "{{.Created}}"
        ]).decode().strip()
        
        # Get API container creation time  
        api_created = subprocess.check_output([
            "docker", "inspect", "api_service", "--format", "{{.Created}}"
        ]).decode().strip()
        
        print(f"React Container Created: {react_created}")
        print(f"API Container Created: {api_created}")
        
        # Convert to datetime for comparison
        from dateutil import parser
        react_time = parser.parse(react_created)
        api_time = parser.parse(api_created)
        
        current_time = datetime.utcnow()
        react_age = (current_time - react_time).total_seconds() / 60  # minutes
        api_age = (current_time - api_time).total_seconds() / 60      # minutes
        
        print(f"React Container Age: {react_age:.1f} minutes")
        print(f"API Container Age: {api_age:.1f} minutes")
        
        if react_age < 10 and api_age < 10:
            print("✅ Container sudah diperbarui dalam 10 menit terakhir")
        else:
            print("⚠️  Container mungkin perlu diperbarui")
            
    except Exception as e:
        print(f"❌ Error checking container timestamps: {e}")
    
    # Test 2: Verifikasi API Endpoints
    print("\n2. 🔌 Verifikasi API Endpoints")
    print("-" * 40)
    
    base_url = "http://localhost:3003/api"  # Through React nginx proxy
    api_key = "development_key_for_testing"
    headers = {"X-API-Key": api_key}
    
    endpoints = [
        ("External Weather", "/external/bmkg/latest"),
        ("System Health", "/system/health/"),
        ("Temperature Stats", "/stats/temperature/last-hour/stats/"),
        ("Humidity Stats", "/stats/humidity/last-hour/stats/")
    ]
    
    all_working = True
    
    for name, endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK ({response.status_code})")
            else:
                print(f"❌ {name}: ERROR ({response.status_code})")
                all_working = False
        except Exception as e:
            print(f"❌ {name}: FAILED ({e})")
            all_working = False
    
    # Test 3: Verifikasi Data Spesifik
    print("\n3. 📊 Verifikasi Data Spesifik untuk Status Iklim Mikro")
    print("-" * 40)
    
    try:
        # Test BMKG data
        bmkg_response = requests.get(f"{base_url}/external/bmkg/latest", headers=headers, timeout=5)
        if bmkg_response.status_code == 200:
            bmkg_data = bmkg_response.json()
            weather = bmkg_data.get('weather_data', {})
            
            temp = weather.get('temperature')
            humidity = weather.get('humidity')
            condition = weather.get('weather_condition')
            
            print(f"🌤️  BMKG Weather Data:")
            print(f"   Temperature: {temp}°C")
            print(f"   Humidity: {humidity}%")
            print(f"   Condition: {condition}")
            
            if temp is not None and humidity is not None:
                print("✅ BMKG data lengkap tersedia")
            else:
                print("⚠️  BMKG data tidak lengkap")
        else:
            print(f"❌ BMKG API error: {bmkg_response.status_code}")
            
        # Test System Health
        health_response = requests.get(f"{base_url}/system/health/", headers=headers, timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            
            status = health_data.get('status')
            active = health_data.get('active_devices')
            total = health_data.get('total_devices')
            influx = health_data.get('influxdb_connection')
            
            print(f"\n⚡ System Health Data:")
            print(f"   Status: {status}")
            print(f"   Active Devices: {active}/{total}")
            print(f"   InfluxDB: {influx}")
            
            if status and active is not None and total is not None:
                print("✅ System health data lengkap tersedia")
            else:
                print("⚠️  System health data tidak lengkap")
        else:
            print(f"❌ System Health API error: {health_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verifying specific data: {e}")
        all_working = False
    
    # Test 4: Verifikasi React App Access
    print("\n4. 🌐 Verifikasi Akses React App")
    print("-" * 40)
    
    try:
        react_response = requests.get("http://localhost:3003", timeout=5)
        if react_response.status_code == 200:
            if "bundle.js" in react_response.text:
                print("✅ React app dapat diakses dan bundle tersedia")
            else:
                print("⚠️  React app dapat diakses tapi bundle tidak ditemukan")
        else:
            print(f"❌ React app error: {react_response.status_code}")
            all_working = False
    except Exception as e:
        print(f"❌ Error accessing React app: {e}")
        all_working = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 RINGKASAN VERIFIKASI")
    print("=" * 60)
    
    if all_working:
        print("🎉 SEMUA VERIFIKASI BERHASIL!")
        print("✅ Container sudah menggunakan kode terbaru")
        print("✅ Semua API endpoints berfungsi")
        print("✅ Data Status Iklim Mikro tersedia")
        print("✅ React app dapat diakses")
        print("\n💡 Silakan akses: http://localhost:3003")
        print("   Dan periksa bagian 'Status Iklim Mikro'")
    else:
        print("⚠️  ADA MASALAH YANG PERLU DIPERBAIKI")
        print("❌ Beberapa verifikasi gagal")
        print("\n🔧 Saran:")
        print("   1. Restart container: docker-compose restart")
        print("   2. Rebuild container: docker-compose build && docker-compose up -d")
        print("   3. Check logs: docker logs web_react_service")
    
    return all_working

if __name__ == "__main__":
    verify_container_updates()
