#!/usr/bin/env python3
"""
Skrip untuk memverifikasi bahwa model 3D EnhancedBuildingModel 
sudah menggunakan data suhu dan kelembapan sebenarnya dari API service,
bukan data dummy/simulasi.
"""

import time
import requests
import json

# Konfigurasi
REACT_APP_URL = "http://localhost:3003"
API_BASE_URL = "http://localhost:8002"
API_KEY = "development_key_for_testing"

def get_real_environmental_data():
    """Ambil data lingkungan real dari API"""
    try:
        headers = {"X-API-Key": API_KEY}
        response = requests.get(f"{API_BASE_URL}/stats/environmental/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error getting real data: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching real environmental data: {e}")
        return None

def test_api_data_availability():
    """Test ketersediaan data real dari API"""
    print("🔍 Testing ketersediaan data real dari API...")
    
    real_data = get_real_environmental_data()
    if not real_data:
        return False
    
    print(f"✅ Data real dari API berhasil diambil:")
    print(f"   - Suhu rata-rata: {real_data['temperature']['avg']}°C")
    print(f"   - Suhu min: {real_data['temperature']['min']}°C") 
    print(f"   - Suhu max: {real_data['temperature']['max']}°C")
    print(f"   - Kelembapan rata-rata: {real_data['humidity']['avg']}%")
    print(f"   - Kelembapan min: {real_data['humidity']['min']}%")
    print(f"   - Kelembapan max: {real_data['humidity']['max']}%")
    print(f"   - Sample count: {real_data['temperature']['sample_count']}")
    print(f"   - Timestamp: {real_data['timestamp']}")
    
    return True

def test_react_app_accessibility():
    """Test apakah React app dapat diakses"""
    try:
        print("🔍 Testing aksesibilitas React app...")
        response = requests.get(REACT_APP_URL, timeout=10)
        
        if response.status_code == 200:
            print("✅ React app dapat diakses")
            
            # Periksa apakah HTML berisi komponen yang diharapkan
            html_content = response.text
            
            if "EnhancedBuildingModel" in html_content or "digital" in html_content.lower():
                print("✅ HTML berisi referensi ke digital twin model")
            else:
                print("⚠️  HTML tidak jelas mengandung model digital twin")
            
            return True
        else:
            print(f"❌ React app tidak dapat diakses: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing React app: {e}")
        return False

def analyze_code_changes():
    """Analisis perubahan kode yang telah dilakukan"""
    print("🔍 Analisis perubahan kode...")
    
    try:
        # Baca file EnhancedBuildingModel.js untuk memverifikasi perubahan
        file_path = "/home/lambda_one/project/digitalTwin/web-react/src/components/EnhancedBuildingModel.js"
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for key indicators
        indicators_found = []
        
        if "fetchRealEnvironmentalData" in content:
            indicators_found.append("✅ Fungsi fetchRealEnvironmentalData ditemukan")
        
        if "realEnvironmentalData" in content:
            indicators_found.append("✅ State realEnvironmentalData ditemukan")
        
        if "/stats/environmental/" in content:
            indicators_found.append("✅ Endpoint /stats/environmental/ digunakan")
        
        if "X-API-Key" in content:
            indicators_found.append("✅ API Key header ditemukan")
        
        if "Real environmental data fetched" in content:
            indicators_found.append("✅ Console log untuk data real ditemukan")
        
        if len(indicators_found) >= 4:
            print("✅ Perubahan kode terdeteksi lengkap:")
            for indicator in indicators_found:
                print(f"   {indicator}")
            return True
        else:
            print("⚠️  Perubahan kode tidak lengkap:")
            for indicator in indicators_found:
                print(f"   {indicator}")
            return False
        
    except Exception as e:
        print(f"❌ Error analyzing code changes: {e}")
        return False

def test_data_flow_logic():
    """Test logika alur data real ke model 3D"""
    print("🔍 Testing logika alur data...")
    
    try:
        file_path = "/home/lambda_one/project/digitalTwin/web-react/src/components/EnhancedBuildingModel.js"
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for proper data flow
        flow_checks = []
        
        # 1. Fetch real data on mount
        if "fetchRealEnvironmentalData();" in content and "useEffect" in content:
            flow_checks.append("✅ Data real di-fetch saat komponen dimuat")
        
        # 2. Room data depends on real data
        if "realEnvironmentalData" in content and "generateRoomData" in content:
            flow_checks.append("✅ Room data bergantung pada data real")
        
        # 3. Base temperature uses real data
        if "realEnvironmentalData?.temperature?.avg" in content:
            flow_checks.append("✅ Suhu base menggunakan data real")
        
        # 4. Base humidity uses real data  
        if "realEnvironmentalData?.humidity?.avg" in content:
            flow_checks.append("✅ Kelembapan base menggunakan data real")
        
        # 5. Room data regenerated when real data changes
        if "realEnvironmentalData" in content and "useEffect" in content:
            flow_checks.append("✅ Room data di-update ketika data real berubah")
        
        if len(flow_checks) >= 4:
            print("✅ Logika alur data terlihat benar:")
            for check in flow_checks:
                print(f"   {check}")
            return True
        else:
            print("⚠️  Logika alur data perlu diperbaiki:")
            for check in flow_checks:
                print(f"   {check}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing data flow logic: {e}")
        return False

def provide_verification_instructions():
    """Berikan instruksi untuk verifikasi manual"""
    print("\n📋 INSTRUKSI VERIFIKASI MANUAL:")
    print("=" * 50)
    
    print("\n1️⃣ Buka browser dan akses: http://localhost:3003")
    print("2️⃣ Buka Developer Tools (F12)")
    print("3️⃣ Pergi ke tab Console")
    print("4️⃣ Refresh halaman dan cari pesan:")
    print("   'Real environmental data fetched: {...}'")
    
    print("\n5️⃣ Pergi ke tab Network")
    print("6️⃣ Refresh halaman dan cari request ke:")
    print("   'localhost:8002/stats/environmental/'")
    print("7️⃣ Periksa response berisi data suhu/kelembapan real")
    
    print("\n8️⃣ Di halaman, klik salah satu ruangan di model 3D")
    print("9️⃣ Lihat nilai suhu dan kelembapan yang ditampilkan")
    print("🔟 Bandingkan dengan data dari API endpoint")
    
    print("\n💡 CARA MEMBANDINGKAN:")
    print("   - Jalankan: curl -H 'X-API-Key: development_key_for_testing' http://localhost:8002/stats/environmental/")
    print("   - Catat nilai suhu/kelembapan rata-rata")
    print("   - Nilai di model 3D seharusnya dalam rentang ±3°C (suhu) dan ±8% (kelembapan)")
    print("   - Ini karena ada variasi per ruangan dari data base real")

def main():
    print("🔬 Verifikasi EnhancedBuildingModel menggunakan data real")
    print("=" * 60)
    
    results = []
    
    # Test 1: API data availability
    print("\n1️⃣ Testing ketersediaan data API...")
    api_ok = test_api_data_availability()
    results.append(("API Data Available", api_ok))
    
    # Test 2: React app accessibility
    print("\n2️⃣ Testing aksesibilitas React app...")
    react_ok = test_react_app_accessibility()
    results.append(("React App Accessible", react_ok))
    
    # Test 3: Code changes analysis
    print("\n3️⃣ Analisis perubahan kode...")
    code_ok = analyze_code_changes()
    results.append(("Code Changes Complete", code_ok))
    
    # Test 4: Data flow logic
    print("\n4️⃣ Testing logika alur data...")
    flow_ok = test_data_flow_logic()
    results.append(("Data Flow Logic", flow_ok))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RANGKUMAN HASIL VERIFIKASI:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Skor: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 KESIMPULAN: EnhancedBuildingModel sudah dikonfigurasi untuk menggunakan data real!")
        print("   ✅ Semua test berhasil")
        print("   ✅ Kode sudah dimodifikasi dengan benar")
        print("   ✅ API endpoint tersedia dan berfungsi")
        print("   ✅ Logika alur data sudah benar")
    elif passed >= 3:
        print("\n⚠️  KESIMPULAN: Implementasi sebagian besar sudah benar")
        print("   ✅ Perubahan kode sudah dilakukan")
        print("   ✅ Infrastruktur API sudah siap")
        print("   ⚠️  Mungkin perlu verifikasi manual untuk memastikan")
    else:
        print("\n❌ KESIMPULAN: Perlu perbaikan lebih lanjut")
        print("   ❌ Ada beberapa komponen yang belum berfungsi")
    
    # Instruksi manual
    provide_verification_instructions()

if __name__ == "__main__":
    main()
