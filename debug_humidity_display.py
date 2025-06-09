#!/usr/bin/env python3
"""
Debug script untuk memeriksa alur data kelembapan eksternal dari API ke React
"""

import requests
import json
import time
from datetime import datetime

def check_api_response():
    """Periksa respons API"""
    print("🔍 Memeriksa respons API BMKG...")
    try:
        # Test direct API
        response = requests.get(
            "http://localhost:8002/external/bmkg/latest",
            headers={"x-api-key": "development_key_for_testing"},
            timeout=10
        )
        print(f"   Status API langsung: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Data diterima: Kelembapan = {data['weather_data']['humidity']}%")
        
        # Test through nginx proxy (like React does)
        response2 = requests.get(
            "http://localhost:3003/api/external/bmkg/latest",
            headers={"x-api-key": "development_key_for_testing"},
            timeout=10
        )
        print(f"   Status melalui nginx: {response2.status_code}")
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"   ✅ Data melalui proxy: Kelembapan = {data2['weather_data']['humidity']}%")
            return data2
        
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def simulate_react_processing(api_data):
    """Simulasikan pemrosesan data seperti yang dilakukan React"""
    print("\n🔄 Simulasi pemrosesan data React...")
    
    if not api_data:
        print("   ❌ Tidak ada data untuk diproses")
        return None
    
    # Ekstrak data seperti kode React
    weather_data = api_data.get('weather_data', {})
    humidity = weather_data.get('humidity')
    
    print(f"   📊 Raw data humidity: {humidity} (type: {type(humidity)})")
    
    # Proses seperti di React component
    if isinstance(humidity, (int, float)):
        formatted_humidity = str(int(humidity))  # toFixed(0) equivalent
        print(f"   ✅ Formatted humidity: {formatted_humidity}%")
        return formatted_humidity
    else:
        print(f"   ❌ Humidity bukan number, menggunakan fallback: 65%")
        return "65"

def check_react_app():
    """Periksa apakah React app dapat diakses"""
    print("\n🌐 Memeriksa akses React app...")
    try:
        response = requests.get("http://localhost:3003", timeout=10)
        print(f"   Status React app: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ React app dapat diakses")
            # Check if there are any error indicators in the HTML
            if "bundle.js" in response.text:
                print("   ✅ Bundle JavaScript terdeteksi")
            return True
        return False
    except Exception as e:
        print(f"   ❌ Error mengakses React: {e}")
        return False

def create_debug_html():
    """Buat file HTML debug untuk testing manual"""
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Debug Kelembapan BMKG</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .result { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .error { background: #ffebee; color: #c62828; }
        .success { background: #e8f5e8; color: #2e7d32; }
    </style>
</head>
<body>
    <h1>🧪 Debug Kelembapan Eksternal BMKG</h1>
    <button onclick="testAPI()">Test API</button>
    <button onclick="testReactLogic()">Test React Logic</button>
    <div id="results"></div>

    <script>
        const API_KEY = 'development_key_for_testing';
        
        async function testAPI() {
            const results = document.getElementById('results');
            results.innerHTML = '<div>🔍 Testing API...</div>';
            
            try {
                const response = await fetch('/api/external/bmkg/latest', {
                    headers: {
                        'x-api-key': API_KEY
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const humidity = data.weather_data?.humidity;
                    
                    results.innerHTML += `
                        <div class="result success">
                            ✅ API Response OK<br>
                            Raw humidity: ${humidity} (${typeof humidity})<br>
                            Formatted: ${typeof humidity === 'number' ? humidity.toFixed(0) : '65'}%
                        </div>
                    `;
                } else {
                    results.innerHTML += `<div class="result error">❌ API Error: ${response.status}</div>`;
                }
            } catch (error) {
                results.innerHTML += `<div class="result error">❌ Fetch Error: ${error.message}</div>`;
            }
        }
        
        async function testReactLogic() {
            const results = document.getElementById('results');
            results.innerHTML += '<div>🔄 Testing React Logic...</div>';
            
            try {
                const response = await fetch('/api/external/bmkg/latest', {
                    headers: {
                        'x-api-key': API_KEY
                    }
                });
                
                const weatherData = await response.json();
                
                // Simulate exact React logic
                const processed = {
                    externalHumidity: typeof weatherData.weather_data?.humidity === 'number' ? 
                        weatherData.weather_data.humidity.toFixed(0) : 
                        (typeof weatherData.humidity === 'number' ? weatherData.humidity.toFixed(0) : '65')
                };
                
                results.innerHTML += `
                    <div class="result">
                        📱 React Logic Output:<br>
                        externalHumidity: ${processed.externalHumidity}%<br>
                        Display: "Kelembapan Luar: ${processed.externalHumidity}%"
                    </div>
                `;
                
            } catch (error) {
                results.innerHTML += `<div class="result error">❌ React Logic Error: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>'''
    
    with open('/home/lambda_one/project/digitalTwin/debug_humidity.html', 'w') as f:
        f.write(html_content)
    
    print("\n📝 File debug HTML dibuat: debug_humidity.html")
    print("   Anda dapat membuka file ini di browser untuk debugging manual")

def main():
    print("=" * 70)
    print("🐛 DEBUG KELEMBAPAN EKSTERNAL - ANALISIS LENGKAP")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Check API
    api_data = check_api_response()
    
    # 2. Simulate React processing
    if api_data:
        formatted_humidity = simulate_react_processing(api_data)
    
    # 3. Check React app
    react_ok = check_react_app()
    
    # 4. Create debug HTML
    create_debug_html()
    
    print("\n" + "=" * 70)
    print("📋 RINGKASAN DEBUG")
    print("=" * 70)
    
    if api_data:
        print("✅ API: Bekerja dengan baik")
        print(f"   Data kelembapan: {api_data['weather_data']['humidity']}%")
    else:
        print("❌ API: Bermasalah")
    
    if react_ok:
        print("✅ React App: Dapat diakses")
    else:
        print("❌ React App: Tidak dapat diakses")
    
    print(f"\n💡 KEMUNGKINAN MASALAH:")
    print("1. Cache browser - coba refresh halaman (Ctrl+F5)")
    print("2. JavaScript error - buka Developer Tools (F12) dan periksa Console")
    print("3. Network error - periksa tab Network di Developer Tools")
    print("4. Data race condition - API dipanggil sebelum component ready")
    
    print(f"\n🔧 LANGKAH DEBUGGING:")
    print("1. Buka http://localhost:3003 di browser")
    print("2. Tekan F12 untuk membuka Developer Tools")
    print("3. Periksa Console untuk error JavaScript")
    print("4. Periksa Network tab untuk melihat API calls")
    print("5. Refresh halaman dan amati network requests")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
