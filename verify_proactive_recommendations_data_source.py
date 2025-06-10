#!/usr/bin/env python3
"""
Script untuk memverifikasi sumber data pada rekomendasi proaktif
- Apakah menggunakan data real dari InfluxDB?
- Atau masih menggunakan data hardcode?
"""

import requests
import json
import sys
from datetime import datetime

# Konfigurasi
API_BASE_URL = "http://localhost:8002"
API_KEY = "development_key_for_testing"

def test_proactive_recommendations_endpoint():
    """Test endpoint rekomendasi proaktif"""
    print("📋 Testing /recommendations/proactive endpoint...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/recommendations/proactive",
            headers={"X-API-Key": API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint berhasil diakses")
            
            # Analisis struktur data
            print(f"📊 Total rekomendasi: {data.get('total_recommendations', 'N/A')}")
            print(f"📈 Priority recommendations: {len(data.get('priority_recommendations', []))}")
            print(f"📋 General recommendations: {len(data.get('general_recommendations', []))}")
            print(f"🏢 Building insights: {len(data.get('building_insights', []))}")
            
            # Cek timestamp untuk melihat apakah real-time
            if 'last_updated' in data:
                print(f"🕒 Last updated: {data['last_updated']}")
                
            # Analisis data room untuk melihat pola hardcode vs real
            statistics = data.get('statistics', {})
            if statistics:
                print("\n🔍 ANALISIS DATA RUANGAN:")
                print(f"   Total ruangan: {statistics.get('total_rooms_monitored', 'N/A')}")
                print(f"   Ruangan optimal: {statistics.get('rooms_optimal', 'N/A')}")
                print(f"   Ruangan kritis: {statistics.get('rooms_critical', 'N/A')}")
                print(f"   Suhu rata-rata: {statistics.get('avg_temperature', 'N/A')}°C")
                print(f"   Kelembapan rata-rata: {statistics.get('avg_humidity', 'N/A')}%")
                
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return None

def analyze_data_source_pattern(data):
    """Analisis pola data untuk menentukan apakah hardcode atau real"""
    print("\n🔍 ANALISIS SUMBER DATA:")
    
    # Cek nilai suhu dan kelembapan dalam rekomendasi
    priority_recs = data.get('priority_recommendations', [])
    
    temperatures = []
    humidities = []
    
    for rec in priority_recs:
        desc = rec.get('description', '')
        
        # Extract temperature values from description
        import re
        temp_matches = re.findall(r'(\d+\.?\d*)°C', desc)
        humidity_matches = re.findall(r'(\d+\.?\d*)%', desc)
        
        for temp in temp_matches:
            try:
                temperatures.append(float(temp))
            except ValueError:
                pass
                
        for hum in humidity_matches:
            try:
                humidities.append(float(hum))
            except ValueError:
                pass
    
    print(f"📊 Suhu terdeteksi dalam rekomendasi: {temperatures}")
    print(f"💧 Kelembapan terdeteksi dalam rekomendasi: {humidities}")
    
    # Analisis pola:
    # 1. Jika nilai decimal (misal: 24.2, 56.0) -> kemungkinan real data
    # 2. Jika nilai bulat (misal: 24, 55) -> kemungkinan hardcode
    # 3. Jika timestamp recent -> real-time
    
    has_decimal_values = any(temp % 1 != 0 for temp in temperatures) or any(hum % 1 != 0 for hum in humidities)
    
    if has_decimal_values:
        print("✅ KEMUNGKINAN DATA REAL: Ditemukan nilai desimal yang presisi")
    else:
        print("⚠️ KEMUNGKINAN HARDCODE: Hanya nilai bulat ditemukan")
    
    # Cek timestamp
    last_updated = data.get('last_updated')
    if last_updated:
        try:
            from datetime import datetime
            updated_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            current_time = datetime.now()
            time_diff = abs((current_time - updated_time.replace(tzinfo=None)).total_seconds())
            
            if time_diff < 60:  # dalam 1 menit
                print("✅ TIMESTAMP REAL-TIME: Data diupdate dalam 1 menit terakhir")
            else:
                print(f"⚠️ TIMESTAMP DELAY: Data diupdate {time_diff:.0f} detik yang lalu")
        except Exception as e:
            print(f"❌ Error parsing timestamp: {e}")

def check_rooms_data_source():
    """Cek apakah data ruangan diambil dari API real atau hardcode"""
    print("\n🏠 CEK SUMBER DATA RUANGAN:")
    
    # Test endpoint yang digunakan dalam get_rooms_data()
    try:
        # Cek apakah ada endpoint rooms yang real
        response = requests.get(
            f"{API_BASE_URL}/rooms/",
            headers={"X-API-Key": API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Endpoint /rooms/ tersedia - kemungkinan menggunakan data real")
            rooms_data = response.json()
            print(f"📊 Jumlah ruangan dari API: {len(rooms_data) if isinstance(rooms_data, list) else 'N/A'}")
        else:
            print("❌ Endpoint /rooms/ tidak tersedia - menggunakan hardcode")
            
        # Cek endpoint stats untuk environmental data
        stats_response = requests.get(
            f"{API_BASE_URL}/stats/temperature/last-hour/stats/",
            headers={"X-API-Key": API_KEY},
            timeout=10
        )
        
        if stats_response.status_code == 200:
            print("✅ Stats endpoint tersedia - environmental data real")
            stats_data = stats_response.json()
            print(f"📈 Data stats: {stats_data}")
        else:
            print("❌ Stats endpoint tidak berfungsi - environmental data mungkin hardcode")
            
    except Exception as e:
        print(f"❌ Error checking data sources: {e}")

def main():
    print("=" * 80)
    print("🔍 VERIFIKASI: Sumber Data Rekomendasi Proaktif")
    print("   Menganalisis apakah menggunakan data real dari InfluxDB/API")
    print("=" * 80)
    
    # Test endpoint
    data = test_proactive_recommendations_endpoint()
    
    if data:
        # Analisis pola data
        analyze_data_source_pattern(data)
        
        # Cek sumber data ruangan
        check_rooms_data_source()
        
        print("\n" + "=" * 80)
        print("📋 KESIMPULAN:")
        
        # Berdasarkan kode yang saya lihat di recommendations_routes.py
        print("   ⚠️ TEMUAN UTAMA:")
        print("   1. ❌ get_rooms_data() menggunakan DATA HARDCODE")
        print("      - Data ruangan di-hardcode dalam fungsi")
        print("      - Nilai temperature/humidity static")
        print("   2. ❌ get_automation_parameters() menggunakan PARAMETER STATIC")
        print("      - Parameter otomasi tidak diambil dari database")
        print("   3. ✅ get_current_environmental_data() mencoba menggunakan stats service")
        print("      - Namun tidak digunakan dalam generate recommendations")
        print("   4. ❌ Rekomendasi dihasilkan dari SIMULASI DATA")
        print("")
        print("   🎯 REKOMENDASI:")
        print("   - Modifikasi get_rooms_data() untuk query InfluxDB real")
        print("   - Integrasikan dengan /rooms/ endpoint yang ada")
        print("   - Gunakan data sensor real-time untuk kondisi ruangan")
        print("=" * 80)
    else:
        print("\n❌ Tidak dapat menganalisis - endpoint tidak dapat diakses")

if __name__ == "__main__":
    main()
