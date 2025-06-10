#!/usr/bin/env python3
"""
Script untuk memeriksa keselarasan antara parameter otomasi dengan peringatan dan rekomendasi
yang dihasilkan oleh sistem Digital Twin
"""

import requests
import json
from datetime import datetime

# Konfigurasi API
API_BASE_URL = "http://localhost:8002"
API_KEY = "development_key_for_testing"
HEADERS = {"X-API-Key": API_KEY}

def get_automation_parameters():
    """Ambil parameter otomasi yang telah diatur"""
    print("🔧 Mengambil parameter otomasi...")
    try:
        response = requests.get(f"{API_BASE_URL}/automation/settings", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Parameter otomasi berhasil diambil")
            return {
                "target_temperature": data.get("target_temperature", 24.0),
                "temperature_tolerance": data.get("temperature_tolerance", 2.0), 
                "target_humidity": data.get("target_humidity", 60.0),
                "humidity_tolerance": data.get("humidity_tolerance", 10.0),
                "alert_threshold_temp": data.get("alert_threshold_temp", 27.0),
                "alert_threshold_humidity": data.get("alert_threshold_humidity", 75.0),
                "temperature_range": {
                    "min": data.get("target_temperature", 24.0) - data.get("temperature_tolerance", 2.0),
                    "max": data.get("target_temperature", 24.0) + data.get("temperature_tolerance", 2.0)
                },
                "humidity_range": {
                    "min": data.get("target_humidity", 60.0) - data.get("humidity_tolerance", 10.0),
                    "max": data.get("target_humidity", 60.0) + data.get("humidity_tolerance", 10.0)
                }
            }
        else:
            print(f"❌ Error mengambil parameter otomasi: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def get_current_environmental_data():
    """Ambil data lingkungan saat ini"""
    print("📊 Mengambil data lingkungan saat ini...")
    try:
        # Ambil data suhu
        temp_response = requests.get(f"{API_BASE_URL}/stats/temperature/last-hour/stats/", headers=HEADERS, timeout=10)
        humidity_response = requests.get(f"{API_BASE_URL}/stats/humidity/last-hour/stats/", headers=HEADERS, timeout=10)
        
        current_data = {}
        
        if temp_response.status_code == 200:
            temp_data = temp_response.json()
            current_data["temperature"] = {
                "avg": temp_data.get("avg_temperature"),
                "min": temp_data.get("min_temperature"), 
                "max": temp_data.get("max_temperature")
            }
            
        if humidity_response.status_code == 200:
            hum_data = humidity_response.json()
            current_data["humidity"] = {
                "avg": hum_data.get("avg_humidity"),
                "min": hum_data.get("min_humidity"),
                "max": hum_data.get("max_humidity")
            }
            
        return current_data
        
    except Exception as e:
        print(f"❌ Error mengambil data lingkungan: {str(e)}")
        return None

def get_recommendations():
    """Ambil rekomendasi dari sistem"""
    print("💡 Mengambil rekomendasi sistem...")
    try:
        response = requests.get(f"{API_BASE_URL}/recommendations/proactive", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error mengambil rekomendasi: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def get_insights_for_room(room="F2", parameter="temperature"):
    """Ambil insights AI untuk ruangan tertentu"""
    print(f"🧠 Mengambil AI insights untuk {room} ({parameter})...")
    try:
        params = {
            "parameter": parameter,
            "location": room,
            "period": "day"
        }
        response = requests.get(f"{API_BASE_URL}/insights/climate-analysis", headers=HEADERS, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error mengambil insights: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def analyze_alignment(automation_params, current_data, recommendations, insights):
    """Analisis keselarasan antara parameter, data, dan rekomendasi"""
    print("\\n🔍 ANALISIS KESELARASAN PARAMETER DAN REKOMENDASI")
    print("=" * 60)
    
    if not automation_params:
        print("❌ Tidak dapat menganalisis: parameter otomasi tidak tersedia")
        return False
    
    alignment_issues = []
    good_alignments = []
    
    # 1. Analisis threshold suhu
    if current_data and "temperature" in current_data:
        temp_data = current_data["temperature"]
        target_temp = automation_params["target_temperature"]
        alert_threshold = automation_params["alert_threshold_temp"]
        temp_range = automation_params["temperature_range"]
        
        print(f"🌡️ ANALISIS SUHU:")
        print(f"   Target: {target_temp}°C")
        print(f"   Rentang optimal: {temp_range['min']:.1f} - {temp_range['max']:.1f}°C")
        print(f"   Ambang peringatan: {alert_threshold}°C")
        
        if temp_data["avg"]:
            current_avg = temp_data["avg"]
            print(f"   Suhu saat ini: {current_avg:.1f}°C")
            
            # Cek apakah suhu saat ini memicu peringatan
            if current_avg > alert_threshold:
                print(f"   ⚠️ Suhu di atas ambang peringatan ({alert_threshold}°C)")
                
                # Cek apakah ada rekomendasi yang sesuai
                if recommendations:
                    temp_recommendations = [r for r in recommendations.get("priority_recommendations", []) 
                                          if r.get("category") == "temperature_control"]
                    if temp_recommendations:
                        good_alignments.append("✅ Ada rekomendasi untuk masalah suhu tinggi")
                        for rec in temp_recommendations:
                            print(f"   📋 Rekomendasi: {rec['title']}")
                    else:
                        alignment_issues.append("❌ Suhu tinggi tapi tidak ada rekomendasi suhu")
            elif current_avg < temp_range["min"]:
                print(f"   ❄️ Suhu di bawah rentang optimal")
            elif current_avg > temp_range["max"]:
                print(f"   🔥 Suhu di atas rentang optimal")
            else:
                print(f"   ✅ Suhu dalam rentang optimal")
                good_alignments.append("✅ Suhu dalam rentang yang diatur")
    
    # 2. Analisis threshold kelembapan  
    if current_data and "humidity" in current_data:
        hum_data = current_data["humidity"]
        target_hum = automation_params["target_humidity"]
        alert_threshold = automation_params["alert_threshold_humidity"]
        hum_range = automation_params["humidity_range"]
        
        print(f"\\n💧 ANALISIS KELEMBAPAN:")
        print(f"   Target: {target_hum}%")
        print(f"   Rentang optimal: {hum_range['min']:.0f} - {hum_range['max']:.0f}%")
        print(f"   Ambang peringatan: {alert_threshold}%")
        
        if hum_data["avg"]:
            current_avg = hum_data["avg"]
            print(f"   Kelembapan saat ini: {current_avg:.0f}%")
            
            # Cek apakah kelembapan saat ini memicu peringatan
            if current_avg > alert_threshold:
                print(f"   ⚠️ Kelembapan di atas ambang peringatan ({alert_threshold}%)")
                
                # Cek apakah ada rekomendasi yang sesuai
                if recommendations:
                    hum_recommendations = [r for r in recommendations.get("priority_recommendations", [])
                                         if r.get("category") == "humidity_control"]
                    if hum_recommendations:
                        good_alignments.append("✅ Ada rekomendasi untuk masalah kelembapan tinggi")
                        for rec in hum_recommendations:
                            print(f"   📋 Rekomendasi: {rec['title']}")
                    else:
                        alignment_issues.append("❌ Kelembapan tinggi tapi tidak ada rekomendasi kelembapan")
            elif current_avg < hum_range["min"]:
                print(f"   🏜️ Kelembapan di bawah rentang optimal")
            elif current_avg > hum_range["max"]:
                print(f"   🌊 Kelembapan di atas rentang optimal")
            else:
                print(f"   ✅ Kelembapan dalam rentang optimal")
                good_alignments.append("✅ Kelembapan dalam rentang yang diatur")
    
    # 3. Analisis insights AI
    if insights and insights.get("success"):
        print(f"\\n🧠 ANALISIS AI INSIGHTS:")
        ai_insights = insights.get("ai_insights", {})
        
        if "recommendations" in ai_insights:
            ai_recommendations = ai_insights["recommendations"]
            print(f"   📝 AI memberikan {len(ai_recommendations)} rekomendasi")
            
            # Cek apakah rekomendasi AI selaras dengan parameter
            for i, rec in enumerate(ai_recommendations[:3], 1):  # Ambil 3 teratas
                print(f"   {i}. {rec}")
                
                # Cek apakah rekomendasi menyebutkan nilai yang selaras dengan parameter
                rec_lower = rec.lower()
                if "suhu" in rec_lower and str(int(automation_params["target_temperature"])) in rec:
                    good_alignments.append("✅ AI merekomendasikan nilai selaras dengan target suhu")
                elif "kelembapan" in rec_lower and str(int(automation_params["target_humidity"])) in rec:
                    good_alignments.append("✅ AI merekomendasikan nilai selaras dengan target kelembapan")
        
        # Cek trend analysis
        trend_summary = insights.get("trend_summary", {})
        if "analysis" in trend_summary:
            trend_direction = trend_summary["analysis"].get("trend_direction", "unknown")
            print(f"   📈 Tren parameter: {trend_direction}")
            
            if trend_direction == "increasing" and current_data:
                if insights.get("parameter") == "temperature" and current_data.get("temperature", {}).get("avg", 0) > automation_params["target_temperature"]:
                    good_alignments.append("✅ Deteksi tren peningkatan suhu selaras dengan kondisi di atas target")
                elif insights.get("parameter") == "humidity" and current_data.get("humidity", {}).get("avg", 0) > automation_params["target_humidity"]:
                    good_alignments.append("✅ Deteksi tren peningkatan kelembapan selaras dengan kondisi di atas target")
    
    print(f"\\n📊 RINGKASAN KESELARASAN:")
    print("=" * 40)
    
    print(f"✅ SELARAS ({len(good_alignments)} item):")
    for item in good_alignments:
        print(f"   {item}")
        
    print(f"\\n❌ TIDAK SELARAS ({len(alignment_issues)} item):")
    for item in alignment_issues:
        print(f"   {item}")
    
    # Hitung persentase keselarasan
    total_checks = len(good_alignments) + len(alignment_issues)
    if total_checks > 0:
        alignment_percentage = (len(good_alignments) / total_checks) * 100
        print(f"\\n📈 TINGKAT KESELARASAN: {alignment_percentage:.1f}%")
        
        if alignment_percentage >= 80:
            print("🎉 EXCELLENT: Sistem sangat selaras!")
        elif alignment_percentage >= 60:
            print("👍 GOOD: Sistem cukup selaras")
        elif alignment_percentage >= 40:
            print("⚠️ FAIR: Perlu beberapa perbaikan")
        else:
            print("❌ POOR: Perlu perbaikan signifikan")
            
        return alignment_percentage >= 60
    
    return False

def main():
    print("🔍 ANALISIS KESELARASAN PARAMETER OTOMASI DAN REKOMENDASI")
    print("=" * 65)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ambil data yang diperlukan
    automation_params = get_automation_parameters()
    current_data = get_current_environmental_data()
    recommendations = get_recommendations()
    insights_temp = get_insights_for_room("F2", "temperature")
    insights_humidity = get_insights_for_room("F2", "humidity")
    
    print("\\n📋 DATA YANG BERHASIL DIAMBIL:")
    print(f"   Parameter otomasi: {'✅' if automation_params else '❌'}")
    print(f"   Data lingkungan: {'✅' if current_data else '❌'}")
    print(f"   Rekomendasi: {'✅' if recommendations else '❌'}")
    print(f"   AI Insights (suhu): {'✅' if insights_temp else '❌'}")
    print(f"   AI Insights (kelembapan): {'✅' if insights_humidity else '❌'}")
    
    # Tampilkan parameter otomasi
    if automation_params:
        print("\\n🔧 PARAMETER OTOMASI YANG DIATUR:")
        print(f"   Target Suhu: {automation_params['target_temperature']}°C")
        print(f"   Target Kelembapan: {automation_params['target_humidity']}%")
        print(f"   Ambang Peringatan Suhu: {automation_params['alert_threshold_temp']}°C")
        print(f"   Ambang Peringatan Kelembapan: {automation_params['alert_threshold_humidity']}%")
        print(f"   Rentang Suhu Optimal: {automation_params['temperature_range']['min']:.1f} - {automation_params['temperature_range']['max']:.1f}°C")
        print(f"   Rentang Kelembapan Optimal: {automation_params['humidity_range']['min']:.0f} - {automation_params['humidity_range']['max']:.0f}%")
    
    # Analisis keselarasan
    is_aligned = analyze_alignment(automation_params, current_data, recommendations, insights_temp)
    
    # Analisis insights kelembapan juga
    if insights_humidity:
        print("\\n" + "="*40)
        print("ANALISIS TAMBAHAN - INSIGHTS KELEMBAPAN")
        analyze_alignment(automation_params, current_data, recommendations, insights_humidity)
    
    print("\\n" + "="*65)
    print("✨ KESIMPULAN:")
    
    if is_aligned:
        print("🎯 Parameter otomasi SELARAS dengan peringatan dan rekomendasi sistem")
        print("✅ Sistem bekerja dengan baik sesuai konfigurasi yang telah diatur")
    else:
        print("⚠️ Ada ketidakselarasan antara parameter dan sistem peringatan/rekomendasi")
        print("🔧 Diperlukan penyesuaian untuk meningkatkan konsistensi sistem")

if __name__ == "__main__":
    main()
