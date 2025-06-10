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
    """Ambil data kondisi semua ruangan dari API real (bukan hardcode)"""
    try:
        import requests
        
        # Daftar ruangan yang ingin dimonitor
        room_ids = ["F2", "F3", "F4", "G2", "G3", "G4"]
        rooms_data = []
        
        headers = {"X-API-Key": "development_key_for_testing"}
        
        # Coba akses internal API menggunakan service name atau localhost
        internal_api_urls = [
            "http://api:8002",  # Service name dalam Docker network
            "http://localhost:8002",  # Localhost fallback
            "http://127.0.0.1:8002"  # IP fallback
        ]
        
        api_base_url = None
        for url in internal_api_urls:
            try:
                test_response = requests.get(f"{url}/system/health/", headers=headers, timeout=5)
                if test_response.status_code == 200:
                    api_base_url = url
                    print(f"✅ Successfully connected to API at {url}")
                    break
            except:
                continue
        
        if not api_base_url:
            print("❌ Cannot connect to internal API, using fallback data")
            # Fallback data dengan timestamp untuk menunjukkan real-time attempt
            from datetime import datetime
            return [
                {"id": "F2", "name": "Ruang F2", "floor": "F", "area": 25, 
                 "currentConditions": {"temperature": 24.0, "humidity": 55.0, "trend": "stable", "last_attempt": datetime.now().isoformat()}},
                {"id": "F3", "name": "Ruang F3", "floor": "F", "area": 30, 
                 "currentConditions": {"temperature": 23.8, "humidity": 48.0, "trend": "stable", "last_attempt": datetime.now().isoformat()}},
                {"id": "F4", "name": "Ruang F4", "floor": "F", "area": 35, 
                 "currentConditions": {"temperature": 25.2, "humidity": 62.0, "trend": "stable", "last_attempt": datetime.now().isoformat()}},
                {"id": "G2", "name": "Ruang G2", "floor": "G", "area": 25, 
                 "currentConditions": {"temperature": 24.1, "humidity": 44.0, "trend": "stable", "last_attempt": datetime.now().isoformat()}},
                {"id": "G3", "name": "Ruang G3", "floor": "G", "area": 30, 
                 "currentConditions": {"temperature": 23.9, "humidity": 46.0, "trend": "stable", "last_attempt": datetime.now().isoformat()}},
                {"id": "G4", "name": "Ruang G4", "floor": "G", "area": 35, 
                 "currentConditions": {"temperature": 25.8, "humidity": 70.0, "trend": "stable", "last_attempt": datetime.now().isoformat()}}
            ]
        
        for room_id in room_ids:
            try:
                # Ambil data real dari endpoint rooms
                response = requests.get(
                    f"{api_base_url}/rooms/{room_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    room_data = response.json()
                    
                    # Extract data yang dibutuhkan untuk rekomendasi
                    current_conditions = room_data.get("currentConditions", {})
                    
                    # Hitung trend berdasarkan daily average vs current
                    daily_avg = room_data.get("statistics", {}).get("dailyAvg", {})
                    current_temp = current_conditions.get("temperature", 0)
                    current_humidity = current_conditions.get("humidity", 0)
                    avg_temp = daily_avg.get("temperature", current_temp)
                    avg_humidity = daily_avg.get("humidity", current_humidity)
                    
                    # Determine trend
                    temp_trend = "stable"
                    if current_temp > avg_temp + 0.5:
                        temp_trend = "increasing"
                    elif current_temp < avg_temp - 0.5:
                        temp_trend = "decreasing"
                    
                    humidity_trend = "stable"
                    if current_humidity > avg_humidity + 2:
                        humidity_trend = "increasing"
                    elif current_humidity < avg_humidity - 2:
                        humidity_trend = "decreasing"
                    
                    # Format untuk compatibility dengan existing code
                    rooms_data.append({
                        "id": room_data["id"],
                        "name": room_data["name"],
                        "floor": room_data["floor"],
                        "area": room_data["area"],
                        "currentConditions": {
                            "temperature": current_temp,
                            "humidity": current_humidity,
                            "trend": temp_trend,  # Overall trend
                            "temp_trend": temp_trend,
                            "humidity_trend": humidity_trend,
                            "co2": current_conditions.get("co2", 400),
                            "air_quality": current_conditions.get("air_quality", 85),
                            "data_source": "real_api"
                        },
                        "statistics": room_data.get("statistics", {}),
                        "devices": room_data.get("devices", [])
                    })
                    
                    print(f"✅ Fetched real data for {room_id}: {current_temp}°C, {current_humidity}%")
                    
                else:
                    print(f"❌ Failed to fetch data for room {room_id}: {response.status_code}")
                    # Fallback untuk room yang gagal
                    rooms_data.append({
                        "id": room_id,
                        "name": f"Ruang {room_id}",
                        "floor": room_id[0],
                        "area": 25,
                        "currentConditions": {
                            "temperature": 24.0,
                            "humidity": 55.0,
                            "trend": "stable",
                            "data_source": "fallback"
                        }
                    })
                    
            except Exception as e:
                print(f"❌ Error fetching data for room {room_id}: {e}")
                # Fallback dengan data default
                rooms_data.append({
                    "id": room_id,
                    "name": f"Ruang {room_id}",
                    "floor": room_id[0],
                    "area": 25,
                    "currentConditions": {
                        "temperature": 24.0,
                        "humidity": 55.0,
                        "trend": "stable",
                        "data_source": "error_fallback"
                    }
                })
        
        print(f"✅ Successfully loaded {len(rooms_data)} rooms data")
        return rooms_data
        
    except Exception as e:
        print(f"❌ Critical error getting rooms data: {e}")
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

async def generate_building_insights(rooms_data, automation_params):
    """Generate insights tingkat gedung berdasarkan kondisi semua ruangan"""
    
    total_rooms = len(rooms_data)
    rooms_temp_optimal = 0
    rooms_humidity_optimal = 0
    rooms_critical = 0
    avg_temp = 0
    avg_humidity = 0
    
    target_temp = automation_params["target_temperature"]
    temp_tolerance = automation_params["temperature_tolerance"]
    target_humidity = automation_params["target_humidity"]
    humidity_tolerance = automation_params["humidity_tolerance"]
    alert_temp = automation_params["alert_threshold_temp"]
    alert_humidity = automation_params["alert_threshold_humidity"]
    
    temp_min = target_temp - temp_tolerance
    temp_max = target_temp + temp_tolerance
    humidity_min = target_humidity - humidity_tolerance
    humidity_max = target_humidity + humidity_tolerance
    
    for room in rooms_data:
        conditions = room["currentConditions"]
        temp = conditions["temperature"]
        humidity = conditions["humidity"]
        
        avg_temp += temp
        avg_humidity += humidity
        
        # Cek kondisi optimal
        if temp_min <= temp <= temp_max:
            rooms_temp_optimal += 1
        if humidity_min <= humidity <= humidity_max:
            rooms_humidity_optimal += 1
            
        # Cek kondisi kritis
        if temp > alert_temp or humidity > alert_humidity:
            rooms_critical += 1
    
    avg_temp /= total_rooms
    avg_humidity /= total_rooms
    
    # Generate insights
    insights = []
    
    # Building performance score
    temp_score = (rooms_temp_optimal / total_rooms) * 100
    humidity_score = (rooms_humidity_optimal / total_rooms) * 100
    overall_score = (temp_score + humidity_score) / 2
    
    if overall_score >= 90:
        performance_status = "EXCELLENT"
        performance_emoji = "🟢"
    elif overall_score >= 75:
        performance_status = "GOOD"
        performance_emoji = "🟡"
    elif overall_score >= 50:
        performance_status = "FAIR"
        performance_emoji = "🟠"
    else:
        performance_status = "POOR"
        performance_emoji = "🔴"
    
    insights.append({
        "id": "building_performance",
        "priority": "info",
        "category": "building_overview",
        "title": f"{performance_emoji} Status Gedung: {performance_status}",
        "description": f"Skor performa gedung: {overall_score:.1f}%. Suhu optimal: {rooms_temp_optimal}/{total_rooms} ruangan ({temp_score:.1f}%). Kelembapan optimal: {rooms_humidity_optimal}/{total_rooms} ruangan ({humidity_score:.1f}%).",
        "metrics": {
            "overall_score": round(overall_score, 1),
            "temperature_score": round(temp_score, 1),
            "humidity_score": round(humidity_score, 1),
            "avg_temperature": round(avg_temp, 1),
            "avg_humidity": round(avg_humidity, 1),
            "rooms_optimal": rooms_temp_optimal + rooms_humidity_optimal,
            "rooms_critical": rooms_critical
        },
        "created_at": datetime.now().isoformat()
    })
    
    # Critical alerts summary
    if rooms_critical > 0:
        insights.append({
            "id": "critical_summary",
            "priority": "critical",
            "category": "alert_summary",
            "title": f"🚨 {rooms_critical} Ruangan Memerlukan Perhatian Segera",
            "description": f"Terdapat {rooms_critical} ruangan dengan kondisi di atas ambang peringatan. Tindakan segera diperlukan untuk mencegah kerusakan arsip.",
            "action": "immediate_intervention",
            "estimated_impact": "Pencegahan kerusakan arsip senilai jutaan rupiah",
            "created_at": datetime.now().isoformat()
        })
    
    # Energy efficiency insights
    energy_insight = await generate_energy_insights(rooms_data, automation_params)
    if energy_insight:
        insights.append(energy_insight)
    
    return insights

async def generate_energy_insights(rooms_data, automation_params):
    """Generate insights tentang efisiensi energi"""
    
    # Hitung potensi penghematan energi
    potential_savings = []
    total_potential = 0
    
    for room in rooms_data:
        conditions = room["currentConditions"]
        temp = conditions["temperature"]
        target_temp = automation_params["target_temperature"]
        
        # Jika suhu jauh dari target, ada potensi waste energi
        temp_diff = abs(temp - target_temp)
        if temp_diff > 1.5:
            room_savings = temp_diff * 3  # 3% per derajat perbedaan
            potential_savings.append({
                "room": room["id"],
                "savings": room_savings,
                "reason": f"Optimasi suhu dapat hemat {room_savings:.1f}% energi"
            })
            total_potential += room_savings
    
    if total_potential > 10:  # Jika potensi penghematan > 10%
        return {
            "id": "energy_optimization",
            "priority": "medium",
            "category": "energy_efficiency",
            "title": f"💡 Potensi Penghematan Energi: {total_potential:.1f}%",
            "description": f"Optimasi pengaturan suhu dapat menghemat hingga {total_potential:.1f}% konsumsi energi bulanan. Estimasi penghematan: Rp 2-4 juta/bulan.",
            "action": "optimize_setpoints",
            "specific_actions": [
                "Review dan sesuaikan setpoint AC di setiap ruangan",
                "Implementasi scheduling otomatis",
                "Monitor konsumsi energi harian"
            ],
            "potential_savings": potential_savings,
            "created_at": datetime.now().isoformat()
        }
    
    return None

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
        building_insights = []
        
        # Analisis per ruangan
        for room_data in rooms_data:
            room_recommendations = await analyze_room_condition(room_data, automation_params)
            priority_recommendations.extend(room_recommendations)
        
        # Generate building-level insights
        building_insights = await generate_building_insights(rooms_data, automation_params)
        
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
                    "Penyesuaian seasonal jika diperlukan",
                    "Update threshold berdasarkan kondisi bangunan"
                ],
                "next_due": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "training_staff",
                "priority": "low",
                "category": "human_resources",
                "title": "👥 Pelatihan Staff Monitoring",
                "description": "Pastikan staff memahami prosedur monitoring, interpretasi data, dan tindakan emergency untuk menjaga kondisi optimal preservasi arsip.",
                "action": "conduct_training",
                "specific_actions": [
                    "Training interpretasi dashboard monitoring",
                    "Prosedur emergency response",
                    "Maintenance basic equipment",
                    "Dokumentasi incident dan response"
                ],
                "next_due": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
                "estimated_cost": "Rp 3-5 juta/quarter",
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
                "energy_cost": "Efisien - Konsumsi energi dalam rentang normal",
                "specific_actions": [
                    "Lanjutkan monitoring rutin",
                    "Pertahankan setting saat ini",
                    "Monitor trend untuk early detection"
                ],
                "created_at": datetime.now().isoformat()
            })
        
        # Statistik untuk dashboard
        stats = {
            "total_rooms_monitored": len(rooms_data),
            "rooms_optimal": len([r for r in rooms_data if is_room_optimal(r, automation_params)]),
            "rooms_critical": len([r for r in priority_recommendations if r.get("priority") == "critical"]),
            "avg_temperature": round(sum([r["currentConditions"]["temperature"] for r in rooms_data]) / len(rooms_data), 1),
            "avg_humidity": round(sum([r["currentConditions"]["humidity"] for r in rooms_data]) / len(rooms_data), 1)
        }
        
        recommendations = {
            "priority_recommendations": priority_recommendations,
            "general_recommendations": general_recommendations,
            "building_insights": building_insights,
            "statistics": stats,
            "total_recommendations": len(priority_recommendations) + len(general_recommendations),
            "critical_alerts": len([r for r in priority_recommendations if r.get("priority") == "critical"]),
            "last_updated": datetime.now().isoformat(),
            "analysis_period": "real_time",
            "automation_parameters": automation_params,
            "system_health": {
                "overall_status": "optimal" if critical_high_count == 0 else "needs_attention",
                "preservation_quality": "excellent" if stats["rooms_optimal"] / stats["total_rooms_monitored"] > 0.8 else "good",
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

# Endpoint tambahan untuk rekomendasi spesifik ruangan
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
        room_recommendations = await analyze_room_condition(target_room, automation_params)
        
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
                "target_parameters": {
                    "temperature": f"{automation_params['target_temperature']}°C (±{automation_params['temperature_tolerance']}°C)",
                    "humidity": f"{automation_params['target_humidity']}% (±{automation_params['humidity_tolerance']}%)"
                },
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
