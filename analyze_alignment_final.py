#!/usr/bin/env python3
"""
Analisis akhir keselarasan antara parameter otomasi dan rekomendasi sistem
"""

import requests
import json

def main():
    print("📋 ANALISIS KESELARASAN PARAMETER OTOMASI & PERINGATAN/REKOMENDASI")
    print("=" * 75)
    
    base_url = "http://localhost:8002"
    headers = {"X-API-Key": "development_key_for_testing"}
    
    # 1. Parameter Otomasi yang digunakan sistem
    print("\n1. 🎯 PARAMETER OTOMASI YANG DIGUNAKAN SISTEM")
    print("-" * 50)
    try:
        response = requests.get(f"{base_url}/automation/settings", headers=headers)
        params = response.json()
        
        target_temp = params.get('target_temperature', 24)
        target_humidity = params.get('target_humidity', 60)
        alert_temp = params.get('alert_threshold_temp', 27)
        alert_humidity = params.get('alert_threshold_humidity', 75)
        temp_tolerance = params.get('temperature_tolerance', 2)
        humidity_tolerance = params.get('humidity_tolerance', 10)
        
        print(f"   🌡️  Target Suhu: {target_temp}°C (±{temp_tolerance}°C)")
        print(f"   💧  Target Kelembaban: {target_humidity}% (±{humidity_tolerance}%)")
        print(f"   🚨  Alert Threshold Suhu: {alert_temp}°C")
        print(f"   🚨  Alert Threshold Kelembaban: {alert_humidity}%")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Kondisi aktual ruangan vs parameter
    print(f"\n2. 🏠 KONDISI AKTUAL RUANGAN VS PARAMETER")
    print("-" * 50)
    
    test_rooms = ['F2', 'G2', 'F3', 'G3']
    room_analysis = []
    
    for room_id in test_rooms:
        try:
            response = requests.get(f"{base_url}/rooms/{room_id}", headers=headers)
            if response.status_code == 200:
                room_data = response.json()
                current = room_data.get('currentConditions', {})
                temp = current.get('temperature')
                humidity = current.get('humidity')
                
                # Analisis kondisi
                temp_status = analyze_temperature(temp, target_temp, temp_tolerance, alert_temp)
                humidity_status = analyze_humidity(humidity, target_humidity, humidity_tolerance, alert_humidity)
                
                room_analysis.append({
                    'room': room_id,
                    'temp': temp,
                    'humidity': humidity,
                    'temp_status': temp_status,
                    'humidity_status': humidity_status
                })
                
                print(f"\n   🏠 Ruangan {room_id}:")
                print(f"      🌡️  Suhu: {temp}°C - {temp_status['description']}")
                print(f"      💧  Kelembaban: {humidity}% - {humidity_status['description']}")
                
        except Exception as e:
            print(f"      ❌ Error room {room_id}: {e}")
    
    # 3. Rekomendasi yang dihasilkan sistem
    print(f"\n3. 🤖 REKOMENDASI YANG DIHASILKAN SISTEM")
    print("-" * 50)
    
    try:
        response = requests.get(f"{base_url}/recommendations/proactive", headers=headers)
        if response.status_code == 200:
            recommendations = response.json()
            priority_recs = recommendations.get('priority_recommendations', [])
            
            print(f"   📊 Total rekomendasi prioritas: {len(priority_recs)}")
            
            for i, rec in enumerate(priority_recs, 1):
                print(f"\n   {i}. {rec.get('title')} (Prioritas: {rec.get('priority')})")
                print(f"      🏠 Ruangan: {rec.get('room')}")
                print(f"      📝 Kategori: {rec.get('category')}")
                print(f"      💬 Deskripsi: {rec.get('description')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Analisis keselarasan
    print(f"\n4. 🔍 ANALISIS KESELARASAN")
    print("-" * 50)
    
    alignment_score = 0
    total_checks = 0
    issues_found = []
    
    # Analisis per ruangan
    for room in room_analysis:
        room_id = room['room']
        temp_status = room['temp_status']
        humidity_status = room['humidity_status']
        
        # Cek apakah ada rekomendasi untuk kondisi yang memerlukan aksi
        room_recs = [rec for rec in priority_recs if room_id in rec.get('room', '')]
        
        # Verifikasi suhu
        if temp_status['needs_action']:
            total_checks += 1
            has_temp_rec = any(['temperature' in rec.get('category', '').lower() or 
                               'suhu' in rec.get('description', '').lower() 
                               for rec in room_recs])
            if has_temp_rec:
                alignment_score += 1
                print(f"   ✅ {room_id}: Kondisi suhu {temp_status['condition']} - Ada rekomendasi yang sesuai")
            else:
                issues_found.append(f"{room_id}: {temp_status['condition']} tapi tidak ada rekomendasi suhu")
                print(f"   ⚠️  {room_id}: Kondisi suhu {temp_status['condition']} - TIDAK ada rekomendasi")
        
        # Verifikasi kelembaban
        if humidity_status['needs_action']:
            total_checks += 1
            has_humidity_rec = any(['humidity' in rec.get('category', '').lower() or 
                                   'kelembaban' in rec.get('description', '').lower() 
                                   for rec in room_recs])
            if has_humidity_rec:
                alignment_score += 1
                print(f"   ✅ {room_id}: Kondisi kelembaban {humidity_status['condition']} - Ada rekomendasi yang sesuai")
            else:
                issues_found.append(f"{room_id}: {humidity_status['condition']} tapi tidak ada rekomendasi kelembaban")
                print(f"   ⚠️  {room_id}: Kondisi kelembaban {humidity_status['condition']} - TIDAK ada rekomendasi")
    
    # 5. Kesimpulan final
    print(f"\n5. 🎯 KESIMPULAN KESELARASAN")
    print("=" * 75)
    
    if total_checks == 0:
        print("ℹ️  SEMUA KONDISI DALAM RENTANG OPTIMAL")
        print("✅ Tidak ada kondisi yang memerlukan peringatan atau rekomendasi")
        print("✅ Sistem berfungsi normal sesuai parameter otomasi")
        alignment_result = "OPTIMAL"
    else:
        alignment_percentage = (alignment_score / total_checks) * 100 if total_checks > 0 else 0
        print(f"📊 Skor Keselarasan: {alignment_score}/{total_checks} ({alignment_percentage:.1f}%)")
        
        if alignment_percentage >= 90:
            print("🎉 KESELARASAN SANGAT BAIK")
            print("✅ Peringatan & Rekomendasi SELARAS dengan Parameter Otomasi")
            alignment_result = "SANGAT_BAIK"
        elif alignment_percentage >= 70:
            print("👍 KESELARASAN BAIK")
            print("✅ Sebagian besar rekomendasi selaras dengan parameter")
            alignment_result = "BAIK"
        else:
            print("⚠️  KESELARASAN PERLU DIPERBAIKI")
            print("❌ Beberapa kondisi tidak mendapat rekomendasi yang sesuai")
            alignment_result = "PERLU_PERBAIKAN"
    
    if issues_found:
        print(f"\n❌ Masalah yang ditemukan:")
        for issue in issues_found:
            print(f"   • {issue}")
    
    # Ringkasan untuk screenshot
    print(f"\n" + "="*75)
    print("📸 RINGKASAN UNTUK DOKUMENTASI")
    print("="*75)
    print(f"• Parameter Target: Suhu {target_temp}°C (±{temp_tolerance}°C), Kelembaban {target_humidity}% (±{humidity_tolerance}%)")
    print(f"• Alert Threshold: Suhu {alert_temp}°C, Kelembaban {alert_humidity}%")
    print(f"• Ruangan yang dianalisis: {len(room_analysis)} ruangan")
    print(f"• Total rekomendasi prioritas: {len(priority_recs)}")
    
    if alignment_result == "OPTIMAL":
        print("• Status: ✅ SISTEM OPTIMAL - Semua kondisi dalam rentang normal")
    elif alignment_result in ["SANGAT_BAIK", "BAIK"]:
        print(f"• Status: ✅ SISTEM SELARAS - Rekomendasi sesuai parameter otomasi")
    else:
        print(f"• Status: ⚠️  PERLU PERBAIKAN - Ada ketidakselarasan")
    
    return alignment_result in ["OPTIMAL", "SANGAT_BAIK", "BAIK"]

def analyze_temperature(temp, target, tolerance, alert_threshold):
    """Analisis status suhu terhadap parameter"""
    if temp is None:
        return {'condition': 'Data tidak tersedia', 'needs_action': False, 'description': 'N/A'}
    
    if temp > alert_threshold:
        return {
            'condition': 'Alert - Terlalu Panas',
            'needs_action': True,
            'description': f'ALERT: {temp}°C > {alert_threshold}°C (threshold)'
        }
    elif temp > target + tolerance:
        return {
            'condition': 'Di atas target',
            'needs_action': True,
            'description': f'TINGGI: {temp}°C > {target + tolerance}°C (target + toleransi)'
        }
    elif temp < target - tolerance:
        return {
            'condition': 'Di bawah target',
            'needs_action': True,
            'description': f'RENDAH: {temp}°C < {target - tolerance}°C (target - toleransi)'
        }
    else:
        return {
            'condition': 'Optimal',
            'needs_action': False,
            'description': f'OPTIMAL: {temp}°C dalam rentang {target-tolerance}°C - {target+tolerance}°C'
        }

def analyze_humidity(humidity, target, tolerance, alert_threshold):
    """Analisis status kelembaban terhadap parameter"""
    if humidity is None:
        return {'condition': 'Data tidak tersedia', 'needs_action': False, 'description': 'N/A'}
    
    if humidity > alert_threshold:
        return {
            'condition': 'Alert - Terlalu Lembab',
            'needs_action': True,
            'description': f'ALERT: {humidity}% > {alert_threshold}% (threshold)'
        }
    elif humidity > target + tolerance:
        return {
            'condition': 'Di atas target',
            'needs_action': True,
            'description': f'TINGGI: {humidity}% > {target + tolerance}% (target + toleransi)'
        }
    elif humidity < target - tolerance:
        return {
            'condition': 'Di bawah target',
            'needs_action': True,
            'description': f'RENDAH: {humidity}% < {target - tolerance}% (target - toleransi)'
        }
    else:
        return {
            'condition': 'Optimal',
            'needs_action': False,
            'description': f'OPTIMAL: {humidity}% dalam rentang {target-tolerance}% - {target+tolerance}%'
        }

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
