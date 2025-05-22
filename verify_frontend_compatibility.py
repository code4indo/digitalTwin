#!/usr/bin/env python3
"""
Verifikasi struktur data API statistik lingkungan untuk kompatibilitas dengan frontend.
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta

# Konfigurasi
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8002")
API_KEY = os.environ.get("API_KEY", "development_key_for_testing")  # API key default dari docker-compose.yml
ENVIRONMENTAL_STATS_ENDPOINT = f"{API_BASE_URL}/stats/environmental/"

# Header untuk autentikasi
headers = {"X-API-Key": API_KEY}

# Struktur data yang diharapkan oleh frontend
EXPECTED_TEMPERATURE_STRUCTURE = {
    "avg": float,
    "min": float,
    "max": float,
    "sample_count": int
}

EXPECTED_HUMIDITY_STRUCTURE = {
    "avg": int,  # Untuk kelembapan, nilai diharapkan dibulatkan ke bilangan bulat
    "min": int,
    "max": int,
    "sample_count": int
}

def validate_response_structure(data):
    """
    Validasi struktur respons API sesuai dengan yang diharapkan oleh frontend.
    
    Struktur yang diharapkan:
    {
        "temperature": {
            "avg": <number>,
            "min": <number>,
            "max": <number>,
            "sample_count": <number>
        },
        "humidity": {
            "avg": <number>,
            "min": <number>,
            "max": <number>,
            "sample_count": <number>
        },
        "timestamp": <string>
    }
    """
    # Verifikasi kunci utama
    required_keys = ["temperature", "humidity", "timestamp"]
    for key in required_keys:
        if key not in data:
            print(f"[ERROR] Kunci '{key}' tidak ditemukan dalam respons.")
            return False
    
    # Verifikasi struktur temperature
    if "temperature" in data:
        temp_keys = ["avg", "min", "max", "sample_count"]
        for key in temp_keys:
            if key not in data["temperature"]:
                print(f"[ERROR] Kunci '{key}' tidak ditemukan dalam data temperatur.")
                return False
    
    # Verifikasi struktur humidity
    if "humidity" in data:
        hum_keys = ["avg", "min", "max", "sample_count"]
        for key in hum_keys:
            if key not in data["humidity"]:
                print(f"[ERROR] Kunci '{key}' tidak ditemukan dalam data kelembapan.")
                return False
    
    # Verifikasi tipe data
    is_valid = True
    
    # Verifikasi temperature
    temp = data["temperature"]
    if temp["avg"] is not None and not isinstance(temp["avg"], (int, float)):
        print(f"[ERROR] 'avg' temperature bukan angka: {temp['avg']}")
        is_valid = False
    if temp["min"] is not None and not isinstance(temp["min"], (int, float)):
        print(f"[ERROR] 'min' temperature bukan angka: {temp['min']}")
        is_valid = False
    if temp["max"] is not None and not isinstance(temp["max"], (int, float)):
        print(f"[ERROR] 'max' temperature bukan angka: {temp['max']}")
        is_valid = False
    if not isinstance(temp["sample_count"], int):
        print(f"[ERROR] 'sample_count' temperature bukan integer: {temp['sample_count']}")
        is_valid = False
    
    # Verifikasi humidity
    hum = data["humidity"]
    if hum["avg"] is not None and not isinstance(hum["avg"], (int, float)):
        print(f"[ERROR] 'avg' humidity bukan angka: {hum['avg']}")
        is_valid = False
    if hum["min"] is not None and not isinstance(hum["min"], (int, float)):
        print(f"[ERROR] 'min' humidity bukan angka: {hum['min']}")
        is_valid = False
    if hum["max"] is not None and not isinstance(hum["max"], (int, float)):
        print(f"[ERROR] 'max' humidity bukan angka: {hum['max']}")
        is_valid = False
    if not isinstance(hum["sample_count"], int):
        print(f"[ERROR] 'sample_count' humidity bukan integer: {hum['sample_count']}")
        is_valid = False
    
    # Validasi timestamp
    if not isinstance(data["timestamp"], str):
        print(f"[ERROR] 'timestamp' bukan string: {data['timestamp']}")
        is_valid = False
    
    return is_valid

def test_frontend_compatibility():
    """Menguji kompatibilitas data API dengan kebutuhan frontend"""
    print("\n==== Menguji Kompatibilitas Data API dengan Frontend ====")
    
    try:
        response = requests.get(ENVIRONMENTAL_STATS_ENDPOINT, headers=headers)
        
        if response.status_code != 200:
            print(f"[ERROR] API mengembalikan status code non-200: {response.status_code}")
            print(f"Detail: {response.text}")
            return False
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"[ERROR] Gagal mendecode respons JSON: {e}")
            return False
        
        print(f"Data respons: {json.dumps(data, indent=2)}")
        
        if validate_response_structure(data):
            print("[SUKSES] Struktur data API sesuai dengan yang diharapkan oleh frontend.")
            
            # Periksa nilai kelembapan (seharusnya bilangan bulat)
            if data["humidity"]["avg"] is not None:
                humidity_avg = data["humidity"]["avg"]
                if humidity_avg != int(humidity_avg):
                    print(f"[PERINGATAN] Nilai kelembapan rata-rata ({humidity_avg}) bukan bilangan bulat.")
                else:
                    print(f"[SUKSES] Nilai kelembapan rata-rata adalah bilangan bulat: {int(humidity_avg)}%")
            
            # Periksa nilai suhu (seharusnya 1 desimal)
            if data["temperature"]["avg"] is not None:
                temp_avg = data["temperature"]["avg"]
                temp_str = str(temp_avg)
                if '.' in temp_str and len(temp_str.split('.')[1]) != 1:
                    print(f"[PERINGATAN] Nilai suhu rata-rata ({temp_avg}) tidak diformat dengan 1 desimal.")
                else:
                    print(f"[SUKSES] Nilai suhu rata-rata diformat dengan benar: {temp_avg}°C")
            
            return True
        else:
            print("[ERROR] Struktur data API tidak sesuai dengan yang diharapkan oleh frontend.")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Gagal terhubung ke API: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan tak terduga: {e}")
        return False

if __name__ == "__main__":
    print("==========================================================")
    print("VERIFIKASI KOMPATIBILITAS API DENGAN FRONTEND")
    print("==========================================================")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Waktu Pengujian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==========================================================")
    
    result = test_frontend_compatibility()
    
    print("\n==========================================================")
    print(f"HASIL PENGUJIAN: {'SUKSES' if result else 'GAGAL'}")
    print("==========================================================")
    
    sys.exit(0 if result else 1)
