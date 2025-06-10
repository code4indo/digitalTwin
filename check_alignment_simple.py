#!/usr/bin/env python3
"""
Script sederhana untuk memverifikasi keselarasan parameter otomasi dengan rekomendasi
"""

import requests
import json
from datetime import datetime

def main():
    print("🔍 VERIFIKASI KESELARASAN PARAMETER OTOMASI")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    headers = {"X-API-Key": "development_key_for_testing"}
    
    # 1. Ambil parameter otomasi
    print("1. Parameter Otomasi Saat Ini:")
    try:
        response = requests.get(f"{base_url}/automation/settings", headers=headers)
        if response.status_code == 200:
            params = response.json()
            print(f"   ✅ Target Suhu: {params.get('target_temperature')}°C")
            print(f"   ✅ Target Kelembaban: {params.get('target_humidity')}%")
            print(f"   ✅ Alert Threshold Suhu: {params.get('alert_threshold_temp')}°C")
            print(f"   ✅ Alert Threshold Kelembaban: {params.get('alert_threshold_humidity')}%")
            print(f"   ✅ Toleransi Suhu: {params.get('temperature_tolerance')}°C")
            print(f"   ✅ Toleransi Kelembaban: {params.get('humidity_tolerance')}%")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Test beberapa ruangan
    print(f"\n2. Verifikasi Keselarasan per Ruangan:")
    
    test_rooms = ['F2', 'G2', 'F3']  # Test 3 ruangan
    alignment_issues = []
    
    for room_code in test_rooms:
        print(f"\n   🏠 Ruangan {room_code}:")
        
        # Ambil data sensor
        try:
            response = requests.get(f"{base_url}/room/{room_code}/current", headers=headers)
            if response.status_code == 200:
                sensor_data = response.json()
                temp = sensor_data.get('temperature')
                humidity = sensor_data.get('humidity')
                print(f"      📊 Suhu: {temp}°C, Kelembaban: {humidity}%")
                
                # Ambil rekomendasi
                response = requests.get(f"{base_url}/recommendations/{room_code}", headers=headers)
                if response.status_code == 200:
                    recommendations = response.json()
                    print(f"      📋 Rekomendasi: {len(recommendations)} item")
                    
                    # Analisis keselarasan
                    issues = analyze_alignment(params, temp, humidity, recommendations, room_code)
                    if issues:
                        alignment_issues.extend(issues)
                        print(f"      ⚠️  {len(issues)} masalah keselarasan:")
                        for issue in issues:
                            print(f"         - {issue}")
                    else:
                        print(f"      ✅ Selaras dengan parameter otomasi")
                        
                        # Tampilkan beberapa rekomendasi
                        if recommendations:
                            print(f"      📝 Contoh rekomendasi:")
                            for i, rec in enumerate(recommendations[:2], 1):
                                print(f"         {i}. {rec.get('recommendation', 'N/A')[:60]}...")
                else:
                    print(f"      ❌ Error ambil rekomendasi: {response.status_code}")
            else:
                print(f"      ❌ Error ambil data sensor: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # 3. Ringkasan
    print(f"\n3. RINGKASAN:")
    print("=" * 60)
    
    if not alignment_issues:
        print("🎉 HASIL: SISTEM SELARAS")
        print("✅ Peringatan & Rekomendasi sudah sesuai dengan Parameter Otomasi")
        print("✅ Semua ruangan yang ditest menunjukkan konsistensi")
    else:
        print("⚠️  HASIL: DITEMUKAN MASALAH KESELARASAN")
        print(f"❌ {len(alignment_issues)} masalah ditemukan:")
        for i, issue in enumerate(alignment_issues, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n📋 Rekomendasi Perbaikan:")
        print("   1. Periksa logika di routes/recommendations_routes.py")
        print("   2. Pastikan parameter otomasi digunakan dalam generate rekomendasi")
        print("   3. Verifikasi algoritma deteksi kondisi tidak optimal")
    
    # 4. Test perubahan parameter (optional)
    print(f"\n4. TEST PERSISTENSI PARAMETER:")
    test_parameter_persistence(base_url, headers, params)

def analyze_alignment(params, temp, humidity, recommendations, room_code):
    """Analisis keselarasan antara parameter dan rekomendasi"""
    
    issues = []
    
    if temp is None or humidity is None:
        return ["Data sensor tidak tersedia"]
    
    target_temp = params.get('target_temperature', 24)
    target_humidity = params.get('target_humidity', 60)
    alert_temp = params.get('alert_threshold_temp', 27)
    alert_humidity = params.get('alert_threshold_humidity', 75)
    temp_tolerance = params.get('temperature_tolerance', 2)
    humidity_tolerance = params.get('humidity_tolerance', 10)
    
    # Gabungkan semua teks rekomendasi
    rec_texts = [rec.get('recommendation', '').lower() for rec in recommendations]
    all_text = ' '.join(rec_texts)
    
    # Cek kondisi alert
    if temp > alert_temp:
        if not any(['suhu' in text and ('tinggi' in text or 'panas' in text or 'ac' in text or 'dingin' in text) for text in rec_texts]):
            issues.append(f"Suhu {temp}°C > alert threshold {alert_temp}°C tapi tidak ada rekomendasi pendinginan")
    
    if humidity > alert_humidity:
        if not any(['kelembaban' in text and ('tinggi' in text or 'lembab' in text) for text in rec_texts]):
            issues.append(f"Kelembaban {humidity}% > alert threshold {alert_humidity}% tapi tidak ada rekomendasi")
    
    # Cek kondisi di luar target (tapi belum alert)
    if abs(temp - target_temp) > temp_tolerance and temp <= alert_temp:
        if temp < target_temp - temp_tolerance:
            if not any(['suhu' in text and ('rendah' in text or 'dingin' in text or 'hangat' in text) for text in rec_texts]):
                issues.append(f"Suhu {temp}°C terlalu rendah dari target {target_temp}°C tapi tidak ada rekomendasi pemanasan")
        else:
            if not any(['suhu' in text and ('tinggi' in text or 'panas' in text) for text in rec_texts]):
                issues.append(f"Suhu {temp}°C terlalu tinggi dari target {target_temp}°C tapi tidak ada rekomendasi pendinginan")
    
    return issues

def test_parameter_persistence(base_url, headers, original_params):
    """Test apakah perubahan parameter tersimpan dan digunakan"""
    
    # Simpan parameter test
    test_params = original_params.copy()
    test_params['target_temperature'] = 23.0  # Ubah sedikit
    
    try:
        print("   📝 Testing penyimpanan parameter...")
        response = requests.post(f"{base_url}/automation/settings", json=test_params, headers=headers)
        
        if response.status_code == 200:
            # Verifikasi tersimpan
            response = requests.get(f"{base_url}/automation/settings", headers=headers)
            if response.status_code == 200:
                saved = response.json()
                if saved.get('target_temperature') == test_params['target_temperature']:
                    print("   ✅ Parameter berhasil disimpan dan dipersist")
                else:
                    print("   ❌ Parameter tidak tersimpan dengan benar")
            
            # Kembalikan parameter asli
            requests.post(f"{base_url}/automation/settings", json=original_params, headers=headers)
            print("   🔄 Parameter asli dikembalikan")
        else:
            print(f"   ❌ Error menyimpan parameter: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error test persistensi: {e}")

if __name__ == "__main__":
    main()
