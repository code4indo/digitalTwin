#!/usr/bin/env python3
"""
Script untuk memverifikasi keselarasan antara parameter otomasi dengan peringatan dan rekomendasi
yang dihasilkan oleh sistem Digital Twin.
"""

import requests
import json
import sys
from datetime import datetime

def test_automation_alignment():
    """Test keselarasan parameter otomasi dengan rekomendasi dan peringatan"""
    
    base_url = "http://localhost:8002"
    headers = {"X-API-Key": "development_key_for_testing"}
    results = {
        "automation_parameters": None,
        "rooms_tested": [],
        "alignment_issues": [],
        "success": True
    }
    
    print("🔍 Memverifikasi keselarasan Parameter Otomasi dengan Peringatan & Rekomendasi")
    print("=" * 80)
    
    # 1. Ambil parameter otomasi saat ini
    try:
        print("1. Mengambil parameter otomasi...")
        response = requests.get(f"{base_url}/automation/settings", headers=headers)
        if response.status_code == 200:
            automation_params = response.json()
            results["automation_parameters"] = automation_params
            print(f"✅ Parameter otomasi berhasil diambil")
            print(f"   - Suhu target: {automation_params.get('target_temperature', 'N/A')}°C")
            print(f"   - Kelembaban target: {automation_params.get('target_humidity', 'N/A')}%")
            print(f"   - Threshold suhu alert: {automation_params.get('alert_threshold_temp', 'N/A')}°C")
            print(f"   - Threshold kelembaban alert: {automation_params.get('alert_threshold_humidity', 'N/A')}%")
        else:
            print(f"❌ Gagal mengambil parameter otomasi: {response.status_code}")
            results["success"] = False
            return results
    except Exception as e:
        print(f"❌ Error mengambil parameter otomasi: {e}")
        results["success"] = False
        return results
    
    # 2. Ambil daftar ruangan
    try:
        print("\n2. Mengambil daftar ruangan...")
        response = requests.get(f"{base_url}/rooms", headers=headers)
        if response.status_code == 200:
            rooms = response.json()
            print(f"✅ Ditemukan {len(rooms)} ruangan")
        else:
            print(f"❌ Gagal mengambil daftar ruangan: {response.status_code}")
            results["success"] = False
            return results
    except Exception as e:
        print(f"❌ Error mengambil daftar ruangan: {e}")
        results["success"] = False
        return results
    
    # 3. Test setiap ruangan
    print("\n3. Memverifikasi keselarasan untuk setiap ruangan...")
    for room in rooms[:3]:  # Test 3 ruangan pertama untuk efisiensi
        room_code = room.get('room_code', room.get('code', 'unknown'))
        print(f"\n   🏠 Testing ruangan: {room_code}")
        
        # Ambil data sensor terkini
        try:
            response = requests.get(f"{base_url}/room/{room_code}/current", headers=headers)
            if response.status_code == 200:
                sensor_data = response.json()
                current_temp = sensor_data.get('temperature')
                current_humidity = sensor_data.get('humidity')
                
                print(f"      📊 Data sensor saat ini:")
                print(f"         - Suhu: {current_temp}°C")
                print(f"         - Kelembaban: {current_humidity}%")
                
                # Ambil rekomendasi
                response = requests.get(f"{base_url}/recommendations/{room_code}", headers=headers)
                if response.status_code == 200:
                    recommendations = response.json()
                    print(f"      📋 Rekomendasi: {len(recommendations)} item")
                    
                    # Verifikasi keselarasan
                    alignment_check = verify_recommendation_alignment(
                        automation_params, current_temp, current_humidity, recommendations, room_code
                    )
                    
                    if alignment_check["issues"]:
                        results["alignment_issues"].extend(alignment_check["issues"])
                        results["success"] = False
                        print(f"      ⚠️  Ditemukan {len(alignment_check['issues'])} masalah keselarasan")
                        for issue in alignment_check["issues"]:
                            print(f"         - {issue}")
                    else:
                        print(f"      ✅ Rekomendasi selaras dengan parameter otomasi")
                    
                    results["rooms_tested"].append({
                        "room_code": room_code,
                        "sensor_data": {"temperature": current_temp, "humidity": current_humidity},
                        "recommendations_count": len(recommendations),
                        "alignment_issues": alignment_check["issues"]
                    })
                else:
                    print(f"      ❌ Gagal mengambil rekomendasi untuk {room_code}")
            else:
                print(f"      ❌ Gagal mengambil data sensor untuk {room_code}")
        except Exception as e:
            print(f"      ❌ Error testing ruangan {room_code}: {e}")
    
    return results

def verify_recommendation_alignment(automation_params, current_temp, current_humidity, recommendations, room_code):
    """Verifikasi apakah rekomendasi selaras dengan parameter otomasi"""
    
    issues = []
    
    if current_temp is None or current_humidity is None:
        return {"issues": ["Data sensor tidak tersedia"]}
    
    target_temp = automation_params.get('target_temperature', 24)
    target_humidity = automation_params.get('target_humidity', 60)
    temp_threshold = automation_params.get('alert_threshold_temp', 27)
    humidity_threshold = automation_params.get('alert_threshold_humidity', 75)
    temp_tolerance = automation_params.get('temperature_tolerance', 2)
    humidity_tolerance = automation_params.get('humidity_tolerance', 10)
    
    # Cek apakah kondisi saat ini membutuhkan peringatan
    temp_too_high = current_temp > temp_threshold
    humidity_too_high = current_humidity > humidity_threshold
    temp_not_optimal = abs(current_temp - target_temp) > temp_tolerance
    humidity_not_optimal = abs(current_humidity - target_humidity) > humidity_tolerance
    
    # Analisis rekomendasi yang ada
    rec_texts = [rec.get('recommendation', '').lower() for rec in recommendations]
    all_rec_text = ' '.join(rec_texts)
    
    # Cek keselarasan
    if temp_too_high:
        if not any(['suhu' in text and ('tinggi' in text or 'dingin' in text or 'ac' in text) for text in rec_texts]):
            issues.append(f"Suhu {current_temp}°C melebihi threshold {temp_threshold}°C tapi tidak ada rekomendasi pendinginan")
    
    if humidity_too_high:
        if not any(['kelembaban' in text and ('tinggi' in text or 'dehumidifier' in text) for text in rec_texts]):
            issues.append(f"Kelembaban {current_humidity}% melebihi threshold {humidity_threshold}% tapi tidak ada rekomendasi pengurangan kelembaban")
    
    if temp_not_optimal and not temp_too_high:
        if current_temp < target_temp - temp_tolerance:
            if not any(['suhu' in text and ('rendah' in text or 'hangat' in text or 'pemanas' in text) for text in rec_texts]):
                issues.append(f"Suhu {current_temp}°C di bawah target {target_temp}°C tapi tidak ada rekomendasi pemanasan")
        elif current_temp > target_temp + temp_tolerance:
            if not any(['suhu' in text and ('tinggi' in text or 'dingin' in text or 'ac' in text) for text in rec_texts]):
                issues.append(f"Suhu {current_temp}°C di atas target {target_temp}°C tapi tidak ada rekomendasi pendinginan")
    
    return {"issues": issues}

def test_parameter_persistence():
    """Test apakah perubahan parameter otomasi tersimpan dan digunakan"""
    
    print("\n4. Testing persistensi parameter otomasi...")
    base_url = "http://localhost:8002"
    headers = {"X-API-Key": "development_key_for_testing"}
    
    # Simpan parameter original
    response = requests.get(f"{base_url}/automation/settings", headers=headers)
    original_params = response.json() if response.status_code == 200 else {}
    
    # Update parameter dengan nilai test
    test_params = {
        "target_temperature": 22,
        "target_humidity": 55,
        "alert_threshold_temp": 26,
        "alert_threshold_humidity": 70
    }
    
    try:
        print("   📝 Menyimpan parameter test...")
        response = requests.post(f"{base_url}/automation/settings", json=test_params, headers=headers)
        if response.status_code == 200:
            print("   ✅ Parameter test berhasil disimpan")
            
            # Verifikasi parameter tersimpan
            response = requests.get(f"{base_url}/automation/settings", headers=headers)
            if response.status_code == 200:
                saved_params = response.json()
                if saved_params.get('target_temperature') == test_params['target_temperature']:
                    print("   ✅ Parameter test berhasil dipersist")
                else:
                    print("   ❌ Parameter tidak tersimpan dengan benar")
                    return False
            
            # Kembalikan parameter original
            if original_params:
                requests.post(f"{base_url}/automation/settings", json=original_params, headers=headers)
                print("   🔄 Parameter original dikembalikan")
            
            return True
        else:
            print(f"   ❌ Gagal menyimpan parameter: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing persistensi: {e}")
        return False

def main():
    print(f"🚀 Verifikasi Keselarasan Sistem Digital Twin")
    print(f"⏰ Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test alignment
    results = test_automation_alignment()
    
    # Test persistensi
    persistence_ok = test_parameter_persistence()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 RINGKASAN HASIL VERIFIKASI")
    print("=" * 80)
    
    if results["success"] and persistence_ok:
        print("🎉 SISTEM SELARAS - Peringatan & Rekomendasi sesuai dengan Parameter Otomasi")
        print(f"✅ {len(results['rooms_tested'])} ruangan diverifikasi")
        print("✅ Parameter otomasi berfungsi dengan baik")
        print("✅ Persistensi parameter berfungsi")
        return 0
    else:
        print("⚠️  DITEMUKAN MASALAH KESELARASAN")
        print(f"🔍 {len(results['rooms_tested'])} ruangan diverifikasi")
        print(f"❌ {len(results['alignment_issues'])} masalah keselarasan ditemukan")
        
        if results["alignment_issues"]:
            print("\n📋 Detail masalah:")
            for i, issue in enumerate(results["alignment_issues"], 1):
                print(f"   {i}. {issue}")
        
        if not persistence_ok:
            print("❌ Masalah persistensi parameter")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
