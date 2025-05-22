#!/usr/bin/env python3
"""
Script untuk memeriksa koneksi ke API di dalam container dan menguji endpoint baru.
"""

import requests
import json
import os
from urllib.parse import urljoin
import subprocess
import time

# Default URL untuk API di container
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "dev-key-123")  # Sesuaikan dengan API key yang digunakan

def get_docker_container_info():
    """Dapatkan informasi tentang container API yang sedang berjalan."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=digital-twin-api", "--format", "{{.ID}},{{.Ports}}"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("❌ Error menjalankan docker ps")
            return None
        
        # Parse output
        lines = result.stdout.strip().split('\n')
        if not lines or not lines[0]:
            print("❌ Tidak ada container API yang berjalan")
            return None
        
        container_id, ports = lines[0].split(',', 1)
        return {"id": container_id, "ports": ports}
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def check_api_health():
    """Cek apakah API dapat diakses."""
    headers = {"X-API-KEY": API_KEY}
    try:
        # Coba akses health endpoint atau endpoint lain yang ada di API
        url = urljoin(API_BASE_URL, "/system/health/")
        print(f"Memeriksa health pada {url}...")
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"✅ API dapat diakses! Status code: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ API mengembalikan status code: {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Tidak dapat terhubung ke API: {str(e)}")
        return False

def test_stats_endpoints():
    """Tes cepat untuk endpoint statistik baru."""
    headers = {"X-API-KEY": API_KEY}
    
    # Cek endpoint temperature stats
    try:
        url = urljoin(API_BASE_URL, "/stats/temperature/")
        print(f"\nMemeriksa endpoint statistik suhu pada {url}...")
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"✅ Endpoint statistik suhu berfungsi! Status code: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Endpoint statistik suhu mengembalikan status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error saat mengakses endpoint statistik suhu: {str(e)}")
    
    # Cek endpoint humidity stats
    try:
        url = urljoin(API_BASE_URL, "/stats/humidity/")
        print(f"\nMemeriksa endpoint statistik kelembapan pada {url}...")
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"✅ Endpoint statistik kelembapan berfungsi! Status code: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Endpoint statistik kelembapan mengembalikan status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error saat mengakses endpoint statistik kelembapan: {str(e)}")
    
    # Cek endpoint environmental stats
    try:
        url = urljoin(API_BASE_URL, "/stats/environmental/")
        print(f"\nMemeriksa endpoint gabungan statistik lingkungan pada {url}...")
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"✅ Endpoint statistik lingkungan berfungsi! Status code: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Endpoint statistik lingkungan mengembalikan status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error saat mengakses endpoint statistik lingkungan: {str(e)}")

if __name__ == "__main__":
    print(f"Memeriksa API pada {API_BASE_URL}...")
    
    # Cek container
    container_info = get_docker_container_info()
    if container_info:
        print(f"Container API ditemukan: {container_info['id']}")
        print(f"Port mapping: {container_info['ports']}")
    else:
        print("Peringatan: Tidak dapat menemukan container Docker untuk API.")
        print("API mungkin berjalan di luar Docker atau dengan nama container yang berbeda.")
    
    # Coba health check
    if check_api_health():
        # Jika health check berhasil, tes endpoint statistik
        time.sleep(1)  # Jeda singkat
        test_stats_endpoints()
    else:
        print("\n❌ Gagal terhubung ke API. Pastikan container API berjalan dan dapat diakses.")
        print("Suggestions:")
        print("1. Periksa status container dengan 'docker ps'")
        print("2. Pastikan port API dipublikasikan dengan benar")
        print("3. Coba ubah API_BASE_URL jika berbeda dari default")
