#!/usr/bin/env python3
"""
Test script untuk memverifikasi endpoint statistik lingkungan berfungsi dengan baik.
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta

# Konfigurasi
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8002")
API_KEY = os.environ.get("API_KEY", "development_key_for_testing")  # API key default dari docker-compose.yml

# Endpoint yang akan diuji
TEMPERATURE_STATS_ENDPOINT = f"{API_BASE_URL}/stats/temperature/"
HUMIDITY_STATS_ENDPOINT = f"{API_BASE_URL}/stats/humidity/"
ENVIRONMENTAL_STATS_ENDPOINT = f"{API_BASE_URL}/stats/environmental/"

# Header untuk autentikasi
headers = {"X-API-Key": API_KEY}

def test_temperature_endpoint():
    """Menguji endpoint statistik suhu"""
    print("\n==== Menguji Endpoint Statistik Suhu ====")
    # Pengujian dengan parameter default
    print("- Pengujian dengan parameter default (24 jam terakhir)")
    response = requests.get(TEMPERATURE_STATS_ENDPOINT, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: SUKSES (HTTP {response.status_code})")
        print(f"  Rata-rata suhu: {data.get('avg_temperature')}°C")
        print(f"  Suhu minimum: {data.get('min_temperature')}°C")
        print(f"  Suhu maksimum: {data.get('max_temperature')}°C")
        print(f"  Jumlah sampel: {data.get('sample_count')}")
    else:
        print(f"  Status: GAGAL (HTTP {response.status_code})")
        print(f"  Detail: {response.text}")
    
    # Pengujian dengan rentang waktu kustom (1 jam terakhir)
    print("\n- Pengujian dengan rentang waktu kustom (1 jam terakhir)")
    start_time = (datetime.now() - timedelta(hours=1)).isoformat()
    params = {"start_time": start_time}
    response = requests.get(TEMPERATURE_STATS_ENDPOINT, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: SUKSES (HTTP {response.status_code})")
        print(f"  Rata-rata suhu: {data.get('avg_temperature')}°C")
        print(f"  Suhu minimum: {data.get('min_temperature')}°C")
        print(f"  Suhu maksimum: {data.get('max_temperature')}°C")
        print(f"  Jumlah sampel: {data.get('sample_count')}")
    else:
        print(f"  Status: GAGAL (HTTP {response.status_code})")
        print(f"  Detail: {response.text}")

def test_humidity_endpoint():
    """Menguji endpoint statistik kelembapan"""
    print("\n==== Menguji Endpoint Statistik Kelembapan ====")
    # Pengujian dengan parameter default
    print("- Pengujian dengan parameter default (24 jam terakhir)")
    response = requests.get(HUMIDITY_STATS_ENDPOINT, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: SUKSES (HTTP {response.status_code})")
        print(f"  Rata-rata kelembapan: {data.get('avg_humidity')}%")
        print(f"  Kelembapan minimum: {data.get('min_humidity')}%")
        print(f"  Kelembapan maksimum: {data.get('max_humidity')}%")
        print(f"  Jumlah sampel: {data.get('sample_count')}")
    else:
        print(f"  Status: GAGAL (HTTP {response.status_code})")
        print(f"  Detail: {response.text}")
    
    # Pengujian dengan rentang waktu kustom (1 jam terakhir)
    print("\n- Pengujian dengan rentang waktu kustom (1 jam terakhir)")
    start_time = (datetime.now() - timedelta(hours=1)).isoformat()
    params = {"start_time": start_time}
    response = requests.get(HUMIDITY_STATS_ENDPOINT, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: SUKSES (HTTP {response.status_code})")
        print(f"  Rata-rata kelembapan: {data.get('avg_humidity')}%")
        print(f"  Kelembapan minimum: {data.get('min_humidity')}%")
        print(f"  Kelembapan maksimum: {data.get('max_humidity')}%")
        print(f"  Jumlah sampel: {data.get('sample_count')}")
    else:
        print(f"  Status: GAGAL (HTTP {response.status_code})")
        print(f"  Detail: {response.text}")

def test_environmental_endpoint():
    """Menguji endpoint statistik lingkungan (gabungan suhu dan kelembapan)"""
    print("\n==== Menguji Endpoint Statistik Lingkungan ====")
    # Pengujian dengan parameter default
    print("- Pengujian dengan parameter default (24 jam terakhir)")
    response = requests.get(ENVIRONMENTAL_STATS_ENDPOINT, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: SUKSES (HTTP {response.status_code})")
        print(f"  Timestamp: {data.get('timestamp')}")
        
        temp_data = data.get('temperature', {})
        print(f"  SUHU:")
        print(f"  - Rata-rata: {temp_data.get('avg')}°C")
        print(f"  - Minimum: {temp_data.get('min')}°C")
        print(f"  - Maksimum: {temp_data.get('max')}°C")
        print(f"  - Jumlah sampel: {temp_data.get('sample_count')}")
        
        hum_data = data.get('humidity', {})
        print(f"  KELEMBAPAN:")
        print(f"  - Rata-rata: {hum_data.get('avg')}%")
        print(f"  - Minimum: {hum_data.get('min')}%")
        print(f"  - Maksimum: {hum_data.get('max')}%")
        print(f"  - Jumlah sampel: {hum_data.get('sample_count')}")
    else:
        print(f"  Status: GAGAL (HTTP {response.status_code})")
        print(f"  Detail: {response.text}")
    
    # Pengujian dengan filter lokasi
    print("\n- Pengujian dengan filter lokasi")
    # Gunakan lokasi R.Arsip-1 sebagai contoh. Ganti dengan lokasi yang valid di sistem Anda
    params = {"locations": ["R.Arsip-1"]}
    response = requests.get(ENVIRONMENTAL_STATS_ENDPOINT, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: SUKSES (HTTP {response.status_code})")
        print(f"  Timestamp: {data.get('timestamp')}")
        
        temp_data = data.get('temperature', {})
        print(f"  SUHU (lokasi: R.Arsip-1):")
        print(f"  - Rata-rata: {temp_data.get('avg')}°C")
        print(f"  - Minimum: {temp_data.get('min')}°C")
        print(f"  - Maksimum: {temp_data.get('max')}°C")
        print(f"  - Jumlah sampel: {temp_data.get('sample_count')}")
        
        hum_data = data.get('humidity', {})
        print(f"  KELEMBAPAN (lokasi: R.Arsip-1):")
        print(f"  - Rata-rata: {hum_data.get('avg')}%")
        print(f"  - Minimum: {hum_data.get('min')}%")
        print(f"  - Maksimum: {hum_data.get('max')}%")
        print(f"  - Jumlah sampel: {hum_data.get('sample_count')}")
    else:
        print(f"  Status: GAGAL (HTTP {response.status_code})")
        print(f"  Detail: {response.text}")

def run_tests():
    print("==========================================================")
    print("PENGUJIAN ENDPOINT API STATISTIK LINGKUNGAN")
    print("==========================================================")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Waktu Pengujian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==========================================================")
    
    test_temperature_endpoint()
    test_humidity_endpoint()
    test_environmental_endpoint()
    
    print("\n==========================================================")
    print("PENGUJIAN SELESAI")
    print("==========================================================")

if __name__ == "__main__":
    run_tests()
