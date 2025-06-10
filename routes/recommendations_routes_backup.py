# routes/recommendations_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
import requests
import asyncio

# Import get_api_key dari api.py daripada mendefinisikan ulang di sini
from utils.auth import get_api_key

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

async def get_current_environmental_data():
    """Ambil data lingkungan saat ini untuk analisis"""
    try:
        # Dalam implementasi nyata, ini akan mengambil dari InfluxDB
        # Untuk demo, kita ambil dari endpoint stats
        from services.stats_service import get_temperature_stats_last_hour, get_humidity_stats_last_hour
        
        temp_data = await get_temperature_stats_last_hour()
        humidity_data = await get_humidity_stats_last_hour()
        
        return {
            "temperature": temp_data,
            "humidity": humidity_data
        }
    except Exception as e:
        print(f"Error getting environmental data: {e}")
        return None

async def get_rooms_data():
    """Ambil data kondisi semua ruangan"""
    try:
        # Simulasi data ruangan yang lebih realistis
        rooms_data = []
        
        # Daftar ruangan yang dimonitor
        room_list = [
            {"id": "F2", "name": "Ruang F2", "floor": "F", "area": 25},
            {"id": "F3", "name": "Ruang F3", "floor": "F", "area": 30},
            {"id": "F4", "name": "Ruang F4", "floor": "F", "area": 35},
            {"id": "G2", "name": "Ruang G2", "floor": "G", "area": 25},
            {"id": "G3", "name": "Ruang G3", "floor": "G", "area": 30},
            {"id": "G4", "name": "Ruang G4", "floor": "G", "area": 35}
        ]
        
        # Data kondisi saat ini untuk setiap ruangan
        conditions = {
            "F2": {"temperature": 24.2, "humidity": 56.0, "trend": "stable"},
            "F3": {"temperature": 24.0, "humidity": 48.1, "trend": "decreasing"},
            "F4": {"temperature": 25.8, "humidity": 62.5, "trend": "increasing"},
            "G2": {"temperature": 24.2, "humidity": 44.3, "trend": "decreasing"},
            "G3": {"temperature": 23.4, "humidity": 45.7, "trend": "stable"},
            "G4": {"temperature": 26.2, "humidity": 72.8, "trend": "increasing"}
        }
        
        for room in room_list:
            room_id = room["id"]
            condition = conditions.get(room_id, {"temperature": 24.0, "humidity": 55.0, "trend": "stable"})
            
            rooms_data.append({
                **room,
                "currentConditions": condition
            })
        
        return rooms_data
    except Exception as e:
        print(f"Error getting rooms data: {e}")
        return []

async def get_automation_parameters():
    """Ambil parameter otomasi yang diatur"""
    # Parameter default dari automation_routes.py
    return {
        "target_temperature": 24.0,
        "temperature_tolerance": 2.0,
        "target_humidity": 60.0,
        "humidity_tolerance": 10.0,
        "alert_threshold_temp": 27.0,
        "alert_threshold_humidity": 75.0
    }

async def analyze_room_condition(room_data, automation_params):
    """Analisis kondisi satu ruangan terhadap parameter otomasi"""
    room_id = room_data["id"]
    room_name = room_data["name"]
    conditions = room_data["currentConditions"]
    
    temp = conditions["temperature"]
    humidity = conditions["humidity"]
    trend = conditions.get("trend", "stable")
    
    target_temp = automation_params["target_temperature"]
    temp_tolerance = automation_params["temperature_tolerance"]
    target_humidity = automation_params["target_humidity"]
    humidity_tolerance = automation_params["humidity_tolerance"]
    alert_temp = automation_params["alert_threshold_temp"]
    alert_humidity = automation_params["alert_threshold_humidity"]
    
    issues = []
    recommendations = []
    
    # Analisis suhu
    temp_min = target_temp - temp_tolerance
    temp_max = target_temp + temp_tolerance
    
    if temp > alert_temp:
        severity = "critical"
        recommendations.append({
            "id": f"temp_critical_{room_id}",
            "priority": "critical",
            "category": "temperature_control",
            "title": f"🚨 CRITICAL: Suhu {room_name} Berbahaya",
            "description": f"Suhu {temp}°C di {room_name} melebihi ambang kritis {alert_temp}°C. TINDAKAN SEGERA diperlukan untuk mencegah kerusakan arsip!",
            "action": "emergency_cooling",
            "room": room_id,
            "severity": "critical",
            "estimated_impact": "Penurunan suhu ke level aman dalam 10-15 menit",
            "preservation_risk": "TINGGI - Potensi kerusakan arsip dalam 30 menit",
            "energy_cost": "Tinggi, namun prioritas keselamatan arsip",
            "specific_actions": [
                f"Segera turunkan setpoint AC {room_name} ke 22°C",
                "Aktifkan mode cooling maksimal",
                "Monitor setiap 5 menit sampai mencapai target",
                "Periksa ventilasi ruangan"
            ],
            "created_at": datetime.now().isoformat()
        })
    elif temp > temp_max:
        recommendations.append({
            "id": f"temp_high_{room_id}",
            "priority": "high",
            "category": "temperature_control",
            "title": f"⚠️ Suhu {room_name} Di Atas Optimal",
            "description": f"Suhu {temp}°C di {room_name} melebihi rentang optimal {temp_min}-{temp_max}°C. Penyesuaian diperlukan untuk mencapai target {target_temp}°C.",
            "action": "adjust_cooling",
            "room": room_id,
            "severity": "medium",
            "estimated_impact": f"Penurunan {temp - target_temp:.1f}°C dalam 20-30 menit",
            "preservation_risk": "SEDANG - Kondisi belum optimal untuk preservasi",
            "energy_cost": "Sedang, efisiensi dapat ditingkatkan",
            "specific_actions": [
                f"Turunkan setpoint AC {room_name} sebesar 1-2°C",
                "Pastikan sirkulasi udara lancar",
                "Monitor progress selama 30 menit"
            ],
            "trend_info": f"Tren: {trend}",
            "created_at": datetime.now().isoformat()
        })
    elif temp < temp_min:
        recommendations.append({
            "id": f"temp_low_{room_id}",
            "priority": "medium",
            "category": "temperature_control",
            "title": f"❄️ Suhu {room_name} Di Bawah Optimal",
            "description": f"Suhu {temp}°C di {room_name} berada di bawah rentang optimal {temp_min}-{temp_max}°C. Penyesuaian diperlukan untuk mencapai target {target_temp}°C.",
            "action": "reduce_cooling",
            "room": room_id,
            "severity": "low",
            "estimated_impact": f"Peningkatan {target_temp - temp:.1f}°C dalam 15-25 menit",
            "preservation_risk": "RENDAH - Masih dalam batas aman",
            "energy_cost": "Penghematan energi dengan mengurangi cooling",
            "specific_actions": [
                f"Naikkan setpoint AC {room_name} sebesar 1°C",
                "Atau kurangi intensitas pendinginan",
                "Monitor untuk stabilitas"
            ],
            "trend_info": f"Tren: {trend}",
            "created_at": datetime.now().isoformat()
        })
    
    # Analisis kelembapan
    humidity_min = target_humidity - humidity_tolerance
    humidity_max = target_humidity + humidity_tolerance
    
    if humidity > alert_humidity:
        recommendations.append({
            "id": f"humidity_critical_{room_id}",
            "priority": "critical",
            "category": "humidity_control",
            "title": f"🚨 CRITICAL: Kelembapan {room_name} Berbahaya",
            "description": f"Kelembapan {humidity}% di {room_name} melebihi ambang kritis {alert_humidity}%. Risiko jamur dan kerusakan arsip sangat tinggi!",
            "action": "emergency_dehumidification",
            "room": room_id,
            "severity": "critical",
            "estimated_impact": f"Penurunan kelembapan ke {target_humidity}% dalam 45-60 menit",
            "preservation_risk": "SANGAT TINGGI - Jamur dapat tumbuh dalam 24-48 jam",
            "energy_cost": "Tinggi, namun prioritas keselamatan arsip",
            "specific_actions": [
                f"Aktifkan dehumidifier {room_name} ke mode maksimal",
                "Tingkatkan sirkulasi udara",
                "Monitor setiap 15 menit",
                "Periksa kebocoran atau sumber kelembapan"
            ],
            "created_at": datetime.now().isoformat()
        })
    elif humidity > humidity_max:
        recommendations.append({
            "id": f"humidity_high_{room_id}",
            "priority": "high",
            "category": "humidity_control",
            "title": f"💧 Kelembapan {room_name} Di Atas Optimal",
            "description": f"Kelembapan {humidity}% di {room_name} melebihi rentang optimal {humidity_min}-{humidity_max}%. Penyesuaian diperlukan untuk mencapai target {target_humidity}%.",
            "action": "increase_dehumidification",
            "room": room_id,
            "severity": "medium",
            "estimated_impact": f"Penurunan {humidity - target_humidity:.0f}% dalam 30-45 menit",
            "preservation_risk": "SEDANG - Perlu perhatian untuk mencegah kondisi memburuk",
            "energy_cost": "Sedang, investasi untuk preservasi jangka panjang",
            "specific_actions": [
                f"Tingkatkan setting dehumidifier {room_name}",
                "Pastikan drainase berfungsi baik",
                "Periksa sumber kelembapan berlebih"
            ],
            "trend_info": f"Tren: {trend}",
            "created_at": datetime.now().isoformat()
        })
    elif humidity < humidity_min:
        recommendations.append({
            "id": f"humidity_low_{room_id}",
            "priority": "medium",
            "category": "humidity_control",
            "title": f"🏜️ Kelembapan {room_name} Di Bawah Optimal",
            "description": f"Kelembapan {humidity}% di {room_name} berada di bawah rentang optimal {humidity_min}-{humidity_max}%. Udara terlalu kering dapat merusak material arsip.",
            "action": "reduce_dehumidification",
            "room": room_id,
            "severity": "medium",
            "estimated_impact": f"Peningkatan {target_humidity - humidity:.0f}% dalam 20-30 menit",
            "preservation_risk": "SEDANG - Material kertas dapat menjadi rapuh",
            "energy_cost": "Penghematan dengan mengurangi dehumidifikasi",
            "specific_actions": [
                f"Kurangi setting dehumidifier {room_name}",
                "Atau aktifkan humidifier jika tersedia",
                "Monitor untuk mencegah over-humidification",
                "Pertimbangkan penambahan tanaman hias"
            ],
            "trend_info": f"Tren: {trend}",
            "created_at": datetime.now().isoformat()
        })
    
    return recommendations

@router.get("/proactive")
async def get_proactive_recommendations(api_key: str = Depends(get_api_key)):
    """
    Mengambil rekomendasi proaktif berdasarkan analisis data sensor dan parameter otomasi
    """
    try:
        # Ambil data terkini dan parameter
        current_data = await get_current_environmental_data()
        automation_params = await get_automation_parameters()
        
        priority_recommendations = []
        general_recommendations = []
        
        if current_data and automation_params:
            # Analisis suhu
            temp_data = current_data.get("temperature", {})
            current_temp = temp_data.get("avg_temperature")
            
            if current_temp is not None:
                target_temp = automation_params["target_temperature"]
                temp_tolerance = automation_params["temperature_tolerance"]
                alert_threshold = automation_params["alert_threshold_temp"]
                
                temp_min = target_temp - temp_tolerance  # 22°C
                temp_max = target_temp + temp_tolerance  # 26°C
                
                if current_temp > alert_threshold:
                    priority_recommendations.append({
                        "id": "temp_critical_high",
                        "priority": "high",
                        "category": "temperature_control",
                        "title": f"Suhu Kritis: {current_temp:.1f}°C",
                        "description": f"Suhu {current_temp:.1f}°C melampaui ambang peringatan {alert_threshold}°C. Diperlukan tindakan segera untuk menurunkan suhu ke target {target_temp}°C",
                        "action": "adjust_hvac_urgent",
                        "room": "Semua ruangan",
                        "estimated_impact": f"Penurunan suhu ke {target_temp}°C dalam 15-30 menit",
                        "energy_saving": "Prioritas preservasi arsip",
                        "created_at": datetime.now().isoformat()
                    })
                elif current_temp > temp_max:
                    priority_recommendations.append({
                        "id": "temp_above_optimal",
                        "priority": "medium",
                        "category": "temperature_control",
                        "title": f"Suhu di Atas Optimal: {current_temp:.1f}°C",
                        "description": f"Suhu {current_temp:.1f}°C berada di atas rentang optimal {temp_min:.1f}-{temp_max:.1f}°C. Disarankan penyesuaian AC untuk mencapai target {target_temp}°C",
                        "action": "adjust_hvac",
                        "room": "Ruangan dengan suhu tinggi",
                        "estimated_impact": f"Penurunan suhu ke rentang {temp_min:.1f}-{temp_max:.1f}°C",
                        "energy_saving": "3-5% efisiensi energi",
                        "created_at": datetime.now().isoformat()
                    })
                elif current_temp < temp_min:
                    priority_recommendations.append({
                        "id": "temp_below_optimal",
                        "priority": "medium", 
                        "category": "temperature_control",
                        "title": f"Suhu di Bawah Optimal: {current_temp:.1f}°C",
                        "description": f"Suhu {current_temp:.1f}°C berada di bawah rentang optimal {temp_min:.1f}-{temp_max:.1f}°C. Pertimbangkan pengurangan pendinginan atau peningkatan pemanas untuk mencapai target {target_temp}°C",
                        "action": "adjust_heating",
                        "room": "Ruangan dengan suhu rendah",
                        "estimated_impact": f"Peningkatan suhu ke rentang {temp_min:.1f}-{temp_max:.1f}°C",
                        "energy_saving": "2-4% efisiensi energi",
                        "created_at": datetime.now().isoformat()
                    })
            
            # Analisis kelembapan
            humidity_data = current_data.get("humidity", {})
            current_humidity = humidity_data.get("avg_humidity")
            
            if current_humidity is not None:
                target_humidity = automation_params["target_humidity"]
                humidity_tolerance = automation_params["humidity_tolerance"]
                alert_threshold = automation_params["alert_threshold_humidity"]
                
                humidity_min = target_humidity - humidity_tolerance  # 50%
                humidity_max = target_humidity + humidity_tolerance  # 70%
                
                if current_humidity > alert_threshold:
                    priority_recommendations.append({
                        "id": "humidity_critical_high",
                        "priority": "high",
                        "category": "humidity_control",
                        "title": f"Kelembapan Kritis: {current_humidity:.0f}%",
                        "description": f"Kelembapan {current_humidity:.0f}% melampaui ambang peringatan {alert_threshold:.0f}%. Risiko kerusakan arsip sangat tinggi. Segera aktifkan dehumidifier untuk mencapai target {target_humidity:.0f}%",
                        "action": "activate_dehumidifier_urgent",
                        "room": "Semua ruangan",
                        "estimated_impact": f"Penurunan kelembapan ke {target_humidity:.0f}% dalam 30-60 menit",
                        "energy_saving": "Prioritas preservasi arsip",
                        "created_at": datetime.now().isoformat()
                    })
                elif current_humidity > humidity_max:
                    priority_recommendations.append({
                        "id": "humidity_above_optimal",
                        "priority": "medium",
                        "category": "humidity_control",
                        "title": f"Kelembapan di Atas Optimal: {current_humidity:.0f}%",
                        "description": f"Kelembapan {current_humidity:.0f}% berada di atas rentang optimal {humidity_min:.0f}-{humidity_max:.0f}%. Disarankan penyesuaian dehumidifier untuk mencapai target {target_humidity:.0f}%",
                        "action": "adjust_dehumidifier",
                        "room": "Ruangan dengan kelembapan tinggi",
                        "estimated_impact": f"Penurunan kelembapan ke rentang {humidity_min:.0f}-{humidity_max:.0f}%",
                        "energy_saving": "5-8% efisiensi energi",
                        "created_at": datetime.now().isoformat()
                    })
                elif current_humidity < humidity_min:
                    priority_recommendations.append({
                        "id": "humidity_below_optimal",
                        "priority": "low",
                        "category": "humidity_control", 
                        "title": f"Kelembapan di Bawah Optimal: {current_humidity:.0f}%",
                        "description": f"Kelembapan {current_humidity:.0f}% berada di bawah rentang optimal {humidity_min:.0f}-{humidity_max:.0f}%. Pertimbangkan pengurangan dehumidifikasi atau aktivasi humidifier untuk mencapai target {target_humidity:.0f}%",
                        "action": "adjust_humidifier",
                        "room": "Ruangan dengan kelembapan rendah",
                        "estimated_impact": f"Peningkatan kelembapan ke rentang {humidity_min:.0f}-{humidity_max:.0f}%",
                        "energy_saving": "3-5% efisiensi energi",
                        "created_at": datetime.now().isoformat()
                    })
        
        # Rekomendasi umum yang selalu ada
        general_recommendations = [
            {
                "id": "rec_003",
                "priority": "low",
                "category": "maintenance",
                "title": "Kalibrasi Sensor Berkala",
                "description": "Lakukan kalibrasi sensor suhu dan kelembapan setiap 3 bulan untuk memastikan akurasi data",
                "action": "schedule_maintenance",
                "next_due": "2025-07-01",
                "created_at": "2025-06-03T20:00:00"
            },
            {
                "id": "rec_004",
                "priority": "low",
                "category": "optimization",
                "title": "Review Parameter Otomasi",
                "description": f"Parameter saat ini: Target suhu {automation_params['target_temperature']}°C, kelembapan {automation_params['target_humidity']}%. Review bulanan untuk optimasi sesuai kondisi musiman",
                "action": "review_settings",
                "next_due": "2025-07-01",
                "created_at": "2025-06-03T20:00:00"
            }
        ]
        
        # Jika tidak ada rekomendasi prioritas, tambahkan status baik
        if not priority_recommendations:
            priority_recommendations.append({
                "id": "status_optimal",
                "priority": "info",
                "category": "status",
                "title": "Kondisi Lingkungan Optimal",
                "description": f"Suhu dan kelembapan berada dalam rentang yang diatur. Target suhu: {automation_params['target_temperature']}°C, target kelembapan: {automation_params['target_humidity']}%",
                "action": "maintain_current",
                "room": "Semua ruangan",
                "estimated_impact": "Preservasi arsip dalam kondisi optimal",
                "energy_saving": "Konsumsi energi efisien",
                "created_at": datetime.now().isoformat()
            })
        
        recommendations = {
            "priority_recommendations": priority_recommendations,
            "general_recommendations": general_recommendations,
            "total_recommendations": len(priority_recommendations) + len(general_recommendations),
            "last_updated": datetime.now().isoformat(),
            "analysis_period": "real_time",
            "automation_parameters": automation_params,
            "current_conditions": {
                "temperature": current_data.get("temperature", {}).get("avg_temperature") if current_data else None,
                "humidity": current_data.get("humidity", {}).get("avg_humidity") if current_data else None
            }
        }
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")

