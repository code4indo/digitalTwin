#!/usr/bin/env python3

import requests
import time
import json

def final_diagnosis_status_iklim_mikro():
    """Final diagnosis dan solusi untuk masalah Status Iklim Mikro"""
    
    print("🔧 DIAGNOSIS FINAL - STATUS IKLIM MIKRO")
    print("=" * 50)
    
    # Check all components
    issues_found = []
    solutions = []
    
    print("\n📋 CHECKLIST KOMPONEN:")
    print("-" * 30)
    
    # 1. API Server Check
    print("1. 🔍 API Server Status...")
    try:
        response = requests.get("http://localhost:8002/system/health/", 
                              headers={"X-API-Key": "development_key_for_testing"}, 
                              timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Server: {data['status']}")
            print(f"   ✅ Active Devices: {data['active_devices']}/{data['total_devices']}")
            print(f"   ✅ InfluxDB: {data['influxdb_connection']}")
        else:
            issues_found.append("API Server tidak merespons dengan benar")
            solutions.append("Restart API container: docker restart api_service")
    except Exception as e:
        issues_found.append(f"API Server tidak dapat diakses: {e}")
        solutions.append("Periksa apakah API container berjalan: docker ps | grep api_service")
    
    # 2. BMKG Data Check
    print("\n2. 🌤️ BMKG Weather Data...")
    try:
        response = requests.get("http://localhost:8002/external/bmkg/latest",
                              headers={"X-API-Key": "development_key_for_testing"},
                              timeout=10)
        if response.status_code == 200:
            data = response.json()
            weather = data.get('weather_data', {})
            print(f"   ✅ Weather Condition: {weather.get('weather_condition', 'N/A')}")
            print(f"   ✅ External Temperature: {weather.get('temperature', 'N/A')}°C")
            print(f"   ✅ External Humidity: {weather.get('humidity', 'N/A')}%")
            print(f"   ✅ Data Source: {data.get('data_source', 'N/A')}")
            
            if weather.get('weather_condition') == 'Tidak Tersedia':
                issues_found.append("BMKG data menunjukkan 'Tidak Tersedia'")
                solutions.append("Periksa koneksi internet dan BMKG collector service")
        else:
            issues_found.append("BMKG API endpoint tidak merespons")
            solutions.append("Restart BMKG collector: docker restart bmkg_collector_service")
    except Exception as e:
        issues_found.append(f"BMKG data tidak dapat diakses: {e}")
        solutions.append("Periksa BMKG collector container")
    
    # 3. React App Check
    print("\n3. ⚛️ React App...")
    try:
        response = requests.get("http://localhost:3003", timeout=5)
        if response.status_code == 200:
            print("   ✅ React App accessible")
            if "bundle.js" in response.text:
                print("   ✅ JavaScript bundle loaded")
            else:
                issues_found.append("JavaScript bundle tidak ditemukan")
                solutions.append("Rebuild React container: docker-compose build web-react")
        else:
            issues_found.append("React App tidak dapat diakses")
            solutions.append("Restart React container: docker restart web_react_service")
    except Exception as e:
        issues_found.append(f"React App error: {e}")
        solutions.append("Periksa React container: docker logs web_react_service")
    
    # 4. API Proxy Check
    print("\n4. 🔄 API Proxy (React → API)...")
    try:
        # Test melalui proxy nginx di React container
        response = requests.get("http://localhost:3003/api/system/health/",
                              headers={"X-API-Key": "development_key_for_testing"},
                              timeout=5)
        if response.status_code == 200:
            print("   ✅ API Proxy working")
        else:
            issues_found.append("API Proxy tidak bekerja")
            solutions.append("Periksa konfigurasi nginx di React container")
    except Exception as e:
        issues_found.append(f"API Proxy error: {e}")
        solutions.append("Restart React container dan periksa nginx config")
    
    # 5. Environmental Data Check
    print("\n5. 📊 Environmental Data...")
    endpoints = [
        ("/api/stats/temperature/last-hour/stats/", "Temperature Stats"),
        ("/api/stats/humidity/last-hour/stats/", "Humidity Stats")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:3003{endpoint}",
                                  headers={"X-API-Key": "development_key_for_testing"},
                                  timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "temperature" in endpoint:
                    print(f"   ✅ {name}: {data.get('avg_temperature', 'N/A')}°C")
                else:
                    print(f"   ✅ {name}: {data.get('avg_humidity', 'N/A')}%")
            else:
                issues_found.append(f"{name} tidak dapat diakses")
                solutions.append("Periksa data sensor di InfluxDB")
        except Exception as e:
            issues_found.append(f"{name} error: {e}")
            solutions.append("Restart container dan periksa koneksi InfluxDB")
    
    # Summary
    print(f"\n📊 DIAGNOSIS SUMMARY")
    print("=" * 30)
    
    if not issues_found:
        print("✅ SEMUA KOMPONEN BEKERJA DENGAN BAIK!")
        print("\n💡 Jika masih ada masalah di browser:")
        print("   1. Clear browser cache (Ctrl+Shift+R)")
        print("   2. Buka Developer Tools (F12) untuk cek console errors")
        print("   3. Periksa Network tab untuk failed API calls")
        print("   4. Coba akses http://localhost:3003/test.html untuk test langsung")
        
        print(f"\n🎉 Status Iklim Mikro should be displaying:")
        print("   • Suhu Rata-rata: dengan data min/max")
        print("   • Kelembapan Rata-rata: dengan data min/max") 
        print("   • Cuaca Eksternal (BMKG): kondisi cuaca real-time")
        print("   • Status Kesehatan Sistem: status perangkat dan InfluxDB")
        
        return True
    else:
        print("❌ ISSUES DITEMUKAN:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 SOLUSI YANG DISARANKAN:")
        for i, solution in enumerate(set(solutions), 1):
            print(f"   {i}. {solution}")
        
        print(f"\n📝 QUICK FIX COMMANDS:")
        print("   # Restart semua container")
        print("   docker-compose down && docker-compose up -d")
        print("")
        print("   # Rebuild React dengan debug enabled")
        print("   docker-compose build web-react && docker-compose up -d web-react")
        print("")
        print("   # Check logs untuk debugging")
        print("   docker logs web_react_service")
        print("   docker logs api_service")
        
        return False

if __name__ == "__main__":
    final_diagnosis_status_iklim_mikro()
