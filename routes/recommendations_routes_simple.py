# routes/recommendations_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
from utils.auth import get_api_key

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

async def get_automation_parameters():
    """Ambil parameter otomasi yang diatur"""
    return {
        "target_temperature": 24.0,
        "temperature_tolerance": 2.0,
        "target_humidity": 60.0,
        "humidity_tolerance": 10.0,
        "alert_threshold_temp": 27.0,
        "alert_threshold_humidity": 75.0
    }

async def get_rooms_data():
    """Ambil data kondisi semua ruangan"""
    # Data simulasi yang lebih realistis
    rooms_data = [
        {"id": "F2", "name": "Ruang F2", "currentConditions": {"temperature": 24.2, "humidity": 56.0, "trend": "stable"}},
        {"id": "F3", "name": "Ruang F3", "currentConditions": {"temperature": 24.0, "humidity": 48.1, "trend": "decreasing"}},
        {"id": "F4", "name": "Ruang F4", "currentConditions": {"temperature": 25.8, "humidity": 62.5, "trend": "increasing"}},
        {"id": "G2", "name": "Ruang G2", "currentConditions": {"temperature": 24.2, "humidity": 44.3, "trend": "decreasing"}},
        {"id": "G3", "name": "Ruang G3", "currentConditions": {"temperature": 23.4, "humidity": 45.7, "trend": "stable"}},
        {"id": "G4", "name": "Ruang G4", "currentConditions": {"temperature": 26.2, "humidity": 72.8, "trend": "increasing"}}
    ]
    return rooms_data

def analyze_room_condition(room_data, automation_params):
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
    
    recommendations = []
    
    # Analisis suhu
    temp_min = target_temp - temp_tolerance
    temp_max = target_temp + temp_tolerance
    
    if temp > alert_temp:
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
            "specific_actions": [
                f"Segera turunkan setpoint AC {room_name} ke 22°C",
                "Aktifkan mode cooling maksimal",
                "Monitor setiap 5 menit sampai mencapai target"
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
            "specific_actions": [
                f"Naikkan setpoint AC {room_name} sebesar 1°C",
                "Atau kurangi intensitas pendinginan"
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
            "specific_actions": [
                f"Aktifkan dehumidifier {room_name} ke mode maksimal",
                "Tingkatkan sirkulasi udara",
                "Monitor setiap 15 menit"
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
            "specific_actions": [
                f"Tingkatkan setting dehumidifier {room_name}",
                "Pastikan drainase berfungsi baik"
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
            "specific_actions": [
                f"Kurangi setting dehumidifier {room_name}",
                "Atau aktifkan humidifier jika tersedia",
                "Monitor untuk mencegah over-humidification"
            ],
            "trend_info": f"Tren: {trend}",
            "created_at": datetime.now().isoformat()
        })
    
    return recommendations

@router.get("/proactive")
async def get_proactive_recommendations(api_key: str = Depends(get_api_key)):
    """
    Mengambil rekomendasi proaktif berdasarkan analisis data sensor dan parameter otomasi
    dengan insights mendalam untuk setiap ruangan dan tingkat gedung
    """
    try:
        # Ambil data terkini dan parameter
        rooms_data = await get_rooms_data()
        automation_params = await get_automation_parameters()
        
        priority_recommendations = []
        general_recommendations = []
        
        # Analisis per ruangan
        for room_data in rooms_data:
            room_recommendations = analyze_room_condition(room_data, automation_params)
            priority_recommendations.extend(room_recommendations)
        
        # Sortir rekomendasi berdasarkan prioritas
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        priority_recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
        
        # Rekomendasi umum yang selalu ada
        general_recommendations = [
            {
                "id": "maintenance_schedule",
                "priority": "low",
                "category": "maintenance",
                "title": "📅 Jadwal Maintenance Preventif",
                "description": "Lakukan maintenance preventif sistem HVAC, sensor, dan peralatan monitoring untuk memastikan performa optimal.",
                "action": "schedule_maintenance",
                "specific_actions": [
                    "Kalibrasi sensor suhu dan kelembapan (bulanan)",
                    "Pembersihan filter AC (2 minggu sekali)",
                    "Pemeriksaan sistem dehumidifier (bulanan)",
                    "Backup data monitoring (harian)"
                ],
                "next_due": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                "estimated_cost": "Rp 1-2 juta/bulan",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "parameter_review",
                "priority": "low",
                "category": "optimization",
                "title": "🔧 Review Parameter Otomasi",
                "description": f"Parameter saat ini optimal untuk preservasi arsip. Target suhu: {automation_params['target_temperature']}°C, kelembapan: {automation_params['target_humidity']}%. Review berkala disarankan sesuai perubahan musim.",
                "action": "quarterly_review",
                "specific_actions": [
                    "Analisis trend bulanan suhu dan kelembapan",
                    "Evaluasi efektivitas parameter saat ini",
                    "Penyesuaian seasonal jika diperlukan"
                ],
                "next_due": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                "created_at": datetime.now().isoformat()
            }
        ]
        
        # Jika tidak ada rekomendasi prioritas critical/high, tambahkan status positif
        critical_high_count = len([r for r in priority_recommendations if r.get("priority") in ["critical", "high"]])
        
        if critical_high_count == 0:
            priority_recommendations.insert(0, {
                "id": "status_excellent",
                "priority": "info",
                "category": "status",
                "title": "✅ Sistem Berfungsi Optimal",
                "description": f"Semua ruangan berada dalam kondisi yang baik untuk preservasi arsip. Target parameter: suhu {automation_params['target_temperature']}°C (±{automation_params['temperature_tolerance']}°C), kelembapan {automation_params['target_humidity']}% (±{automation_params['humidity_tolerance']}%).",
                "action": "maintain_current",
                "room": "Seluruh gedung",
                "estimated_impact": "Preservasi arsip terjaga dengan optimal",
                "preservation_risk": "MINIMAL - Kondisi ideal untuk preservasi jangka panjang",
                "specific_actions": [
                    "Lanjutkan monitoring rutin",
                    "Pertahankan setting saat ini",
                    "Monitor trend untuk early detection"
                ],
                "created_at": datetime.now().isoformat()
            })
        
        # Statistik untuk dashboard
        rooms_optimal = len([r for r in rooms_data if is_room_optimal(r, automation_params)])
        
        stats = {
            "total_rooms_monitored": len(rooms_data),
            "rooms_optimal": rooms_optimal,
            "rooms_critical": len([r for r in priority_recommendations if r.get("priority") == "critical"]),
            "avg_temperature": round(sum([r["currentConditions"]["temperature"] for r in rooms_data]) / len(rooms_data), 1),
            "avg_humidity": round(sum([r["currentConditions"]["humidity"] for r in rooms_data]) / len(rooms_data), 1)
        }
        
        recommendations = {
            "priority_recommendations": priority_recommendations,
            "general_recommendations": general_recommendations,
            "statistics": stats,
            "total_recommendations": len(priority_recommendations) + len(general_recommendations),
            "critical_alerts": len([r for r in priority_recommendations if r.get("priority") == "critical"]),
            "last_updated": datetime.now().isoformat(),
            "analysis_period": "real_time",
            "automation_parameters": automation_params,
            "system_health": {
                "overall_status": "optimal" if critical_high_count == 0 else "needs_attention",
                "preservation_quality": "excellent" if rooms_optimal / len(rooms_data) > 0.8 else "good",
                "energy_efficiency": "good"
            }
        }
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")

def is_room_optimal(room_data, automation_params):
    """Check if room conditions are within optimal range"""
    conditions = room_data["currentConditions"]
    temp = conditions["temperature"]
    humidity = conditions["humidity"]
    
    target_temp = automation_params["target_temperature"]
    temp_tolerance = automation_params["temperature_tolerance"]
    target_humidity = automation_params["target_humidity"]
    humidity_tolerance = automation_params["humidity_tolerance"]
    
    temp_optimal = (target_temp - temp_tolerance) <= temp <= (target_temp + temp_tolerance)
    humidity_optimal = (target_humidity - humidity_tolerance) <= humidity <= (target_humidity + humidity_tolerance)
    
    return temp_optimal and humidity_optimal

@router.get("/{room_id}")
async def get_room_recommendations(room_id: str, api_key: str = Depends(get_api_key)):
    """
    Mengambil rekomendasi spesifik untuk satu ruangan
    """
    try:
        rooms_data = await get_rooms_data()
        automation_params = await get_automation_parameters()
        
        # Cari data ruangan yang diminta
        target_room = None
        for room in rooms_data:
            if room["id"] == room_id:
                target_room = room
                break
        
        if not target_room:
            raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
        
        # Analisis kondisi ruangan
        room_recommendations = analyze_room_condition(target_room, automation_params)
        
        # Jika tidak ada issue, berikan status optimal
        if not room_recommendations:
            room_recommendations.append({
                "id": f"status_optimal_{room_id}",
                "priority": "info",
                "category": "status",
                "title": f"✅ {target_room['name']} dalam Kondisi Optimal",
                "description": f"Kondisi lingkungan {target_room['name']} berada dalam rentang optimal untuk preservasi arsip.",
                "room": room_id,
                "current_conditions": target_room["currentConditions"],
                "created_at": datetime.now().isoformat()
            })
        
        return {
            "room_id": room_id,
            "room_name": target_room["name"],
            "current_conditions": target_room["currentConditions"],
            "recommendations": room_recommendations,
            "total_recommendations": len(room_recommendations),
            "room_status": "optimal" if not any(r.get("priority") in ["critical", "high"] for r in room_recommendations) else "needs_attention",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching room recommendations: {str(e)}")
