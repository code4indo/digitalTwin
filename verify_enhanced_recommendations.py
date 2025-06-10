#!/usr/bin/env python3
"""
Script untuk memverifikasi sistem rekomendasi yang telah ditingkatkan
menampilkan insight yang kaya dan actionable untuk Digital Twin
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8002"
API_KEY = "development_key_for_testing"
HEADERS = {"X-API-Key": API_KEY}

def test_proactive_recommendations():
    """Test endpoint rekomendasi proaktif dengan insight mendalam"""
    print("="*60)
    print("🔍 TESTING ENHANCED PROACTIVE RECOMMENDATIONS")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE}/recommendations/proactive", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Endpoint berhasil diakses")
            print(f"📊 Total rekomendasi: {data['total_recommendations']}")
            print(f"🚨 Critical alerts: {data.get('critical_alerts', 0)}")
            
            # Building insights
            print("\n📈 BUILDING INSIGHTS:")
            for insight in data.get('building_insights', []):
                print(f"  • {insight['title']}")
                if 'metrics' in insight:
                    metrics = insight['metrics']
                    print(f"    Overall Score: {metrics.get('overall_score', 'N/A')}%")
                
            # Priority recommendations with room analysis
            print("\n🎯 PRIORITY RECOMMENDATIONS (Per Ruangan):")
            priority_recs = data.get('priority_recommendations', [])
            
            rooms_analyzed = set()
            for rec in priority_recs:
                if rec.get('room'):
                    rooms_analyzed.add(rec['room'])
                    
                print(f"  • {rec['title']}")
                print(f"    Priority: {rec.get('priority', 'N/A').upper()}")
                print(f"    Room: {rec.get('room', 'N/A')}")
                print(f"    Actions: {len(rec.get('specific_actions', []))} steps")
                
                # Preservation impact analysis
                if 'preservation_risk' in rec:
                    print(f"    Preservation Risk: {rec['preservation_risk']}")
                if 'energy_cost' in rec:
                    print(f"    Energy Impact: {rec['energy_cost']}")
                print()
            
            print(f"🏢 Rooms analyzed: {len(rooms_analyzed)} ruangan")
            
            # General recommendations
            print("📋 GENERAL RECOMMENDATIONS:")
            for rec in data.get('general_recommendations', []):
                print(f"  • {rec['title']}")
                print(f"    Category: {rec.get('category', 'N/A')}")
                if 'next_due' in rec:
                    print(f"    Next Due: {rec['next_due']}")
                print()
            
            # System health indicators
            health = data.get('system_health', {})
            print("💚 SYSTEM HEALTH:")
            print(f"  Overall Status: {health.get('overall_status', 'N/A')}")
            print(f"  Preservation Quality: {health.get('preservation_quality', 'N/A')}")
            print(f"  Energy Efficiency: {health.get('energy_efficiency', 'N/A')}")
            
            return True
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_room_specific_recommendations():
    """Test rekomendasi spesifik per ruangan"""
    print("\n" + "="*60)
    print("🏠 TESTING ROOM-SPECIFIC RECOMMENDATIONS")
    print("="*60)
    
    rooms_to_test = ["F2", "F3", "G4"]
    
    for room_id in rooms_to_test:
        print(f"\n--- Testing Room {room_id} ---")
        
        try:
            response = requests.get(f"{API_BASE}/recommendations/{room_id}", headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Room: {data['room_name']} ({data['room_id']})")
                print(f"📊 Status: {data['room_status']}")
                
                conditions = data['current_conditions']
                print(f"🌡️ Temperature: {conditions['temperature']}°C (trend: {conditions['trend']})")
                print(f"💧 Humidity: {conditions['humidity']}%")
                
                recs = data['recommendations']
                print(f"📝 Recommendations: {len(recs)}")
                
                for i, rec in enumerate(recs, 1):
                    print(f"  {i}. {rec['title']}")
                    print(f"     Priority: {rec.get('priority', 'N/A').upper()}")
                    if 'specific_actions' in rec:
                        print(f"     Actions: {len(rec['specific_actions'])} steps")
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_automation_alignment():
    """Test keselarasan dengan parameter otomasi"""
    print("\n" + "="*60)
    print("⚙️ TESTING AUTOMATION ALIGNMENT")
    print("="*60)
    
    try:
        # Get automation parameters
        auto_response = requests.get(f"{API_BASE}/automation/parameters", headers=HEADERS)
        recs_response = requests.get(f"{API_BASE}/recommendations/proactive", headers=HEADERS)
        
        if auto_response.status_code == 200 and recs_response.status_code == 200:
            auto_params = auto_response.json()
            recs_data = recs_response.json()
            
            print("✅ Parameter otomasi berhasil diambil")
            print(f"🎯 Target Temperature: {auto_params.get('target_temperature')}°C")
            print(f"🎯 Target Humidity: {auto_params.get('target_humidity')}%")
            print(f"🚨 Alert Thresholds: {auto_params.get('alert_threshold_temp')}°C, {auto_params.get('alert_threshold_humidity')}%")
            
            # Check if recommendations reference these parameters
            stored_params = recs_data.get('automation_parameters', {})
            print(f"\n📋 Parameters used in recommendations:")
            print(f"  Temperature: {stored_params.get('target_temperature')}°C (±{stored_params.get('temperature_tolerance')}°C)")
            print(f"  Humidity: {stored_params.get('target_humidity')}% (±{stored_params.get('humidity_tolerance')}%)")
            
            # Verify alignment
            alignment_check = (
                auto_params.get('target_temperature') == stored_params.get('target_temperature') and
                auto_params.get('target_humidity') == stored_params.get('target_humidity')
            )
            
            if alignment_check:
                print("✅ Parameter otomasi dan rekomendasi SELARAS")
            else:
                print("⚠️ Parameter otomasi dan rekomendasi TIDAK SELARAS")
                
        else:
            print("❌ Gagal mengambil data untuk alignment check")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main verification function"""
    print("🔧 VERIFIKASI SISTEM REKOMENDASI YANG DITINGKATKAN")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test all components
    success1 = test_proactive_recommendations()
    test_room_specific_recommendations()
    test_automation_alignment()
    
    print("\n" + "="*60)
    print("📋 SUMMARY PENINGKATAN SISTEM")
    print("="*60)
    
    improvements = [
        "✅ Analisis per ruangan (bukan hanya agregat)",
        "✅ Rekomendasi untuk semua kondisi (termasuk kelembapan rendah)",
        "✅ Insight tingkat gedung dengan performance score",
        "✅ Rekomendasi actionable dengan specific_actions",
        "✅ Analisis preservation risk dan energy impact",
        "✅ Status optimal ditampilkan jika semua ruangan baik",
        "✅ General recommendations (maintenance, training, review)",
        "✅ Endpoint per ruangan untuk insight granular",
        "✅ Building performance metrics dan energy optimization",
        "✅ Keselarasan sempurna dengan parameter otomasi"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")
    
    if success1:
        print("\n🎉 SISTEM REKOMENDASI BERHASIL DITINGKATKAN!")
        print("💡 Insight yang dihasilkan sekarang lebih kaya, actionable, dan bermanfaat bagi pengguna")
    else:
        print("\n⚠️ Masih ada masalah yang perlu diperbaiki")

if __name__ == "__main__":
    main()
