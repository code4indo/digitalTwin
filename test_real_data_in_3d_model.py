#!/usr/bin/env python3
"""
Skrip untuk memverifikasi bahwa model 3D EnhancedBuildingModel 
sudah menggunakan data suhu dan kelembapan sebenarnya dari API service,
bukan data dummy/simulasi.
"""

import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

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

def test_3d_model_real_data():
    """Test apakah model 3D menggunakan data real"""
    print("🔍 Testing apakah EnhancedBuildingModel menggunakan data real...")
    
    # Ambil data real dari API
    real_data = get_real_environmental_data()
    if not real_data:
        print("❌ Tidak bisa mendapatkan data real dari API")
        return False
    
    print(f"✅ Data real dari API:")
    print(f"   - Suhu rata-rata: {real_data['temperature']['avg']}°C")
    print(f"   - Kelembapan rata-rata: {real_data['humidity']['avg']}%")
    print(f"   - Timestamp: {real_data['timestamp']}")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(REACT_APP_URL)
        
        # Tunggu halaman dimuat
        wait = WebDriverWait(driver, 30)
        
        print("⏳ Menunggu halaman dimuat...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Tunggu model 3D dimuat
        print("⏳ Menunggu model 3D dimuat...")
        time.sleep(10)  # Beri waktu untuk model 3D dan data API dimuat
        
        # Check console logs untuk melihat apakah data real difetch
        logs = driver.get_log('browser')
        real_data_logged = False
        
        for log in logs:
            if 'Real environmental data fetched:' in log['message']:
                real_data_logged = True
                print("✅ Data real berhasil di-fetch dari API (terlihat di console log)")
                break
        
        if not real_data_logged:
            print("⚠️  Tidak ditemukan log fetch data real di console")
        
        # Cari elemen yang menampilkan suhu/kelembapan ruangan
        room_info_found = False
        try:
            # Cari elemen room stats atau room info
            room_elements = driver.find_elements(By.CLASS_NAME, "room-stats")
            if not room_elements:
                room_elements = driver.find_elements(By.CLASS_NAME, "selected-room-details")
            
            if room_elements:
                room_info_found = True
                room_element = room_elements[0]
                room_text = room_element.text
                
                print(f"✅ Ditemukan informasi ruangan:")
                print(f"   {room_text}")
                
                # Ekstrak nilai suhu dari teks
                if "°C" in room_text:
                    lines = room_text.split('\n')
                    for line in lines:
                        if "Suhu:" in line and "°C" in line:
                            temp_str = line.split("Suhu:")[1].replace("°C", "").strip()
                            try:
                                displayed_temp = float(temp_str)
                                real_temp_avg = real_data['temperature']['avg']
                                
                                # Periksa apakah suhu yang ditampilkan berada dalam rentang yang masuk akal
                                # dari data real (±3°C karena ada variasi per ruangan)
                                temp_diff = abs(displayed_temp - real_temp_avg)
                                
                                print(f"   📊 Suhu ditampilkan: {displayed_temp}°C")
                                print(f"   📊 Suhu real API: {real_temp_avg}°C")
                                print(f"   📊 Selisih: {temp_diff:.1f}°C")
                                
                                if temp_diff <= 3.0:
                                    print("✅ Suhu model 3D kemungkinan besar menggunakan data real")
                                    print("   (dalam rentang ±3°C dari data API - variasi wajar per ruangan)")
                                else:
                                    print("⚠️  Suhu model 3D mungkin masih dummy (selisih >3°C dari API)")
                                
                            except ValueError:
                                print(f"⚠️  Tidak bisa parse suhu: {temp_str}")
                        
                        elif "Kelembapan:" in line and "%" in line:
                            humidity_str = line.split("Kelembapan:")[1].replace("%", "").strip()
                            try:
                                displayed_humidity = float(humidity_str)
                                real_humidity_avg = real_data['humidity']['avg']
                                
                                humidity_diff = abs(displayed_humidity - real_humidity_avg)
                                
                                print(f"   📊 Kelembapan ditampilkan: {displayed_humidity}%")
                                print(f"   📊 Kelembapan real API: {real_humidity_avg}%")
                                print(f"   📊 Selisih: {humidity_diff:.1f}%")
                                
                                if humidity_diff <= 8.0:
                                    print("✅ Kelembapan model 3D kemungkinan besar menggunakan data real")
                                    print("   (dalam rentang ±8% dari data API - variasi wajar per ruangan)")
                                else:
                                    print("⚠️  Kelembapan model 3D mungkin masih dummy (selisih >8% dari API)")
                                
                            except ValueError:
                                print(f"⚠️  Tidak bisa parse kelembapan: {humidity_str}")
            
        except Exception as e:
            print(f"⚠️  Error saat mencari elemen room info: {e}")
        
        if not room_info_found:
            print("⚠️  Tidak ditemukan elemen yang menampilkan info ruangan")
        
        # Klik ruangan untuk melihat detail
        try:
            print("⏳ Mencoba mengklik ruangan untuk melihat detail...")
            
            # Cari canvas 3D
            canvas = driver.find_element(By.TAG_NAME, "canvas")
            if canvas:
                # Klik di tengah canvas
                driver.execute_script("arguments[0].click();", canvas)
                time.sleep(3)
                
                # Coba cari informasi ruangan yang muncul setelah klik
                updated_room_elements = driver.find_elements(By.CLASS_NAME, "selected-room-details")
                if updated_room_elements:
                    updated_text = updated_room_elements[0].text
                    print(f"✅ Info ruangan setelah klik:")
                    print(f"   {updated_text}")
                
        except Exception as e:
            print(f"⚠️  Error saat klik ruangan: {e}")
        
        # Check apakah ada error di console
        error_logs = [log for log in logs if log['level'] == 'SEVERE']
        if error_logs:
            print("⚠️  Ditemukan error di console:")
            for error in error_logs[:3]:  # Tampilkan 3 error pertama
                print(f"   - {error['message']}")
        
        driver.quit()
        
        return real_data_logged or room_info_found
        
    except WebDriverException as e:
        print(f"❌ WebDriver error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🔬 Verifikasi EnhancedBuildingModel menggunakan data real")
    print("=" * 60)
    
    # Test API endpoint dulu
    print("1️⃣ Testing API endpoint...")
    real_data = get_real_environmental_data()
    if not real_data:
        print("❌ API endpoint tidak tersedia - test dihentikan")
        return
    
    # Test model 3D
    print("\n2️⃣ Testing model 3D...")
    result = test_3d_model_real_data()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ HASIL: Model 3D kemungkinan sudah menggunakan data real")
        print("   - Data API berhasil diambil")
        print("   - Model 3D menunjukkan indikasi penggunaan data real")
    else:
        print("⚠️  HASIL: Perlu investigasi lebih lanjut")
        print("   - Model 3D mungkin masih menggunakan data dummy")
    
    print("\n💡 Tips:")
    print("   - Periksa Network tab di browser untuk memastikan API call berhasil")
    print("   - Periksa Console log untuk melihat 'Real environmental data fetched'")
    print("   - Bandingkan nilai yang ditampilkan dengan API /stats/environmental/")

if __name__ == "__main__":
    main()
