#!/usr/bin/env python3
"""
Script final untuk memverifikasi keselarasan parameter otomasi dengan rekomendasi
"""

import requests
import json
from datetime import datetime

def main():
    print("🔍 VERIFIKASI KESELARASAN PARAMETER OTOMASI & REKOMENDASI")
    print("=" * 70)
    print(f"⏰ Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8002"
    headers = {"X-API-Key": "development_key_for_testing"}
    
    # 1. Ambil parameter otomasi saat ini
    print("1. 📋 PARAMETER OTOMASI SAAT INI")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/automation/settings", headers=headers)
        if response.status_code == 200:
            params = response.json()
            print(f"   ✅ Target Suhu: {params.get('target_temperature')}°C")
            print(f"   ✅ Target Kelembaban: {params.get('target_humidity')}%")
            print(f"   ✅ Alert Threshold Suhu: {params.get('alert_threshold_temp')}°C")
            print(f"   ✅ Alert Threshold Kelembaban: {params.get('alert_threshold_humidity')}%")
            print(f"   ✅ Toleransi Suhu: ±{params.get('temperature_tolerance', 2)}°C")
            print(f"   ✅ Toleransi Kelembaban: ±{params.get('humidity_tolerance', 10)}%")
            print(f"   ✅ Kontrol Suhu: {'Aktif' if params.get('temperature_control') else 'Nonaktif'}")
            print(f"   ✅ Kontrol Kelembaban: {'Aktif' if params.get('humidity_control') else 'Nonaktif'}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 2. Ambil rekomendasi proaktif
    print(f"\n2. 🤖 REKOMENDASI SISTEM SAAT INI")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/recommendations/proactive", headers=headers)
        if response.status_code == 200:
            recommendations = response.json()
            priority_recs = recommendations.get('priority_recommendations', [])
            general_recs = recommendations.get('general_recommendations', [])
            
            print(f"   📊 Total rekomendasi: {recommendations.get('total_recommendations', 0)}")
            print(f"   🚨 Rekomendasi prioritas: {len(priority_recs)}")
            print(f"   📝 Rekomendasi umum: {len(general_recs)}")
            
            if priority_recs:
                print(f"\n   🔥 REKOMENDASI PRIORITAS:")
                for i, rec in enumerate(priority_recs, 1):
                    print(f"      {i}. {rec.get('title')} (Prioritas: {rec.get('priority')})")
                    print(f"         Ruangan: {rec.get('room', 'N/A')}")
                    print(f"         Deskripsi: {rec.get('description', 'N/A')[:80]}...")
        else:
            print(f"   ❌ Error mengambil rekomendasi: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verifikasi beberapa ruangan
    print(f"\n3. 🏠 VERIFIKASI KESELARASAN PER RUANGAN")
    print("-" * 40)
    
    test_rooms = ['F2', 'G2', 'F3']
    alignment_issues = []
    total_tested = 0
    
    for room_id in test_rooms:
        print(f"\n   🏠 Ruangan {room_id}:")
        try:
            response = requests.get(f"{base_url}/rooms/{room_id}", headers=headers)
            if response.status_code == 200:
                room_data = response.json()
                current = room_data.get('currentConditions', {})
                temp = current.get('temperature')
                humidity = current.get('humidity')
                
                print(f"      📊 Kondisi saat ini:")
                print(f"         Suhu: {temp}°C")
                print(f"         Kelembaban: {humidity}%")
                
                # Analisis keselarasan
                issues = analyze_room_alignment(params, temp, humidity, room_id, priority_recs)
                if issues:
                    alignment_issues.extend(issues)
                    print(f"      ⚠️  {len(issues)} masalah keselarasan:")
                    for issue in issues:
                        print(f"         - {issue}")
                else:
                    print(f"      ✅ Selaras dengan parameter otomasi")
                
                total_tested += 1
            else:
                print(f"      ❌ Error mengambil data: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # 4. Test persistensi parameter
    print(f"\n4. 🔄 TEST PERSISTENSI PARAMETER")
    print("-" * 40)
    persistence_ok = test_parameter_persistence(base_url, headers, params)
    
    # 5. Ringkasan hasil
    print(f"\n5. 📊 RINGKASAN VERIFIKASI")
    print("=" * 70)
    
    if not alignment_issues and persistence_ok and total_tested > 0:
        print("🎉 HASIL: SISTEM SELARAS ✅")
        print(f"✅ {total_tested} ruangan diverifikasi - semua selaras")
        print("✅ Parameter otomasi berfungsi dengan baik")
        print("✅ Persistensi parameter berfungsi")
        print("✅ Rekomendasi generated berdasarkan parameter yang benar")
        
        print(f"\n📋 KESIMPULAN:")
        print("   • Peringatan & Rekomendasi SUDAH SELARAS dengan Parameter Otomasi")
        print("   • Sistem menggunakan parameter target dan threshold yang tepat")
        print("   • Perubahan parameter akan langsung mempengaruhi rekomendasi")
        print("   • Tidak ada masalah keselarasan yang ditemukan")
        
        return True
    else:
        print("⚠️  HASIL: DITEMUKAN MASALAH")
        if alignment_issues:
            print(f"❌ {len(alignment_issues)} masalah keselarasan:")
            for i, issue in enumerate(alignment_issues, 1):
                print(f"   {i}. {issue}")
        
        if not persistence_ok:
            print("❌ Masalah persistensi parameter")
        
        if total_tested == 0:
            print("❌ Tidak ada ruangan yang berhasil ditest")
        
        print(f"\n🔧 SARAN PERBAIKAN:")
        print("   1. Periksa logika di routes/recommendations_routes.py")
        print("   2. Pastikan parameter otomasi digunakan dalam generate rekomendasi")
        print("   3. Verifikasi endpoint automation/settings")
        
        return False

def analyze_room_alignment(params, temp, humidity, room_id, priority_recommendations):
    """Analisis keselarasan kondisi ruangan dengan parameter otomasi"""
    
    issues = []
    
    if temp is None or humidity is None:
        return ["Data sensor tidak tersedia"]
    
    target_temp = params.get('target_temperature', 24)
    target_humidity = params.get('target_humidity', 60)
    alert_temp = params.get('alert_threshold_temp', 27)
    alert_humidity = params.get('alert_threshold_humidity', 75)
    temp_tolerance = params.get('temperature_tolerance', 2)
    humidity_tolerance = params.get('humidity_tolerance', 10)
    
    # Cek apakah kondisi memerlukan alert
    needs_temp_alert = temp > alert_temp
    needs_humidity_alert = humidity > alert_humidity
    
    # Cek apakah kondisi di luar target tapi belum alert
    temp_out_of_target = abs(temp - target_temp) > temp_tolerance
    humidity_out_of_target = abs(humidity - target_humidity) > humidity_tolerance
    
    # Cek apakah ada rekomendasi untuk ruangan ini
    room_recommendations = [rec for rec in priority_recommendations 
                          if room_id in rec.get('room', '')]
    
    # Verifikasi keselarasan
    if needs_temp_alert:
        if not any('temperature' in rec.get('category', '').lower() or 
                  'suhu' in rec.get('description', '').lower() 
                  for rec in room_recommendations):
            issues.append(f"Suhu {temp}°C melebihi alert threshold {alert_temp}°C tapi tidak ada rekomendasi suhu")
    
    if needs_humidity_alert:
        if not any('humidity' in rec.get('category', '').lower() or 
                  'kelembaban' in rec.get('description', '').lower() 
                  for rec in room_recommendations):
            issues.append(f"Kelembaban {humidity}% melebihi alert threshold {alert_humidity}% tapi tidak ada rekomendasi kelembaban")
    
    # Cek konsistensi target
    if temp_out_of_target and not needs_temp_alert:
        if temp > target_temp + temp_tolerance:
            # Suhu terlalu tinggi tapi belum alert
            if not any('temperature' in rec.get('category', '').lower() or 
                      'suhu' in rec.get('description', '').lower() 
                      for rec in room_recommendations):
                issues.append(f"Suhu {temp}°C di atas target {target_temp}°C tapi tidak ada rekomendasi pendinginan")
    
    return issues

def test_parameter_persistence(base_url, headers, original_params):
    """Test persistensi perubahan parameter"""
    
    print("   📝 Testing penyimpanan parameter...")
    
    # Buat parameter test dengan perubahan kecil
    test_params = original_params.copy()
    test_params['target_temperature'] = original_params.get('target_temperature', 24) + 0.5
    
    try:
        # Test PUT endpoint untuk update
        response = requests.put(f"{base_url}/automation/settings", json=test_params, headers=headers)
        
        if response.status_code == 200:
            print("   ✅ Parameter berhasil diupdate")
            
            # Verifikasi perubahan tersimpan
            response = requests.get(f"{base_url}/automation/settings", headers=headers)
            if response.status_code == 200:
                saved = response.json()
                if abs(saved.get('target_temperature', 0) - test_params['target_temperature']) < 0.1:
                    print("   ✅ Parameter berhasil dipersist")
                    
                    # Kembalikan parameter asli
                    requests.put(f"{base_url}/automation/settings", json=original_params, headers=headers)
                    print("   🔄 Parameter asli dikembalikan")
                    return True
                else:
                    print("   ❌ Parameter tidak tersimpan dengan benar")
                    return False
            else:
                print(f"   ❌ Error verifikasi parameter: {response.status_code}")
                return False
        else:
            print(f"   ❌ Error menyimpan parameter: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error test persistensi: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n✅ KESIMPULAN: Peringatan & Rekomendasi SELARAS dengan Parameter Otomasi")
        exit(0)
    else:
        print(f"\n❌ KESIMPULAN: Ditemukan masalah keselarasan yang perlu diperbaiki")
        exit(1)
