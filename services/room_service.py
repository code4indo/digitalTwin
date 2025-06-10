"""
Service untuk mengelola data ruangan dalam aplikasi Digital Twin.
Versi sementara yang menggunakan data simulasi bervariasi per room.
"""

import logging
import math
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional, Any

# Konfigurasi logging
logger = logging.getLogger(__name__)

# Konstanta untuk room metadata
ROOM_METADATA = {
    "F2": {"name": "Ruang F2", "floor": "F", "area": 25},
    "F3": {"name": "Ruang F3", "floor": "F", "area": 30},
    "F4": {"name": "Ruang F4", "floor": "F", "area": 35},
    "F5": {"name": "Ruang F5", "floor": "F", "area": 28},
    "F6": {"name": "Ruang F6", "floor": "F", "area": 32},
    "G2": {"name": "Ruang G2", "floor": "G", "area": 25},
    "G3": {"name": "Ruang G3", "floor": "G", "area": 30},
    "G4": {"name": "Ruang G4", "floor": "G", "area": 35},
    "G5": {"name": "Ruang G5", "floor": "G", "area": 28},
    "G6": {"name": "Ruang G6", "floor": "G", "area": 32},
    "G7": {"name": "Ruang G7", "floor": "G", "area": 30},
    "G8": {"name": "Ruang G8", "floor": "G", "area": 40},
}

async def get_room_details(room_id: str) -> Dict[str, Any]:
    """
    Mengambil data detail ruangan dengan data simulasi yang bervariasi per room.
    
    Args:
        room_id (str): ID ruangan (contoh: F2, G3, dsb)
        
    Returns:
        Dict[str, Any]: Data ruangan dengan format JSON
    """
    logger.info(f"Mengambil detail ruangan untuk {room_id} (mode simulasi)")
    
    # Ambil metadata dasar ruangan
    if room_id not in ROOM_METADATA:
        logger.error(f"Room ID {room_id} tidak ditemukan dalam metadata")
        return None
        
    room_data = {
        "id": room_id,
        "name": ROOM_METADATA[room_id]["name"],
        "floor": ROOM_METADATA[room_id]["floor"],
        "area": ROOM_METADATA[room_id]["area"]
    }
    
    try:
        # Generate data simulasi yang bervariasi per room
        current_conditions = generate_room_conditions(room_id)
        daily_avg = generate_daily_averages(room_id, current_conditions)
        time_in_optimal_range = generate_optimal_time_percentages(room_id)
        devices = await get_room_devices(room_id)
        
        # Buat struktur data lengkap yang sesuai dengan ekspektasi frontend
        room_data.update({
            "currentConditions": current_conditions,  # Frontend expects currentConditions (camelCase)
            "statistics": {
                "dailyAvg": daily_avg,
                "timeInOptimalRange": time_in_optimal_range
            },
            "devices": devices
        })
        
        return room_data
        
    except Exception as e:
        logger.error(f"Error saat mengambil data ruangan {room_id}: {str(e)}")
        # Return data dasar saja jika terjadi error
        return room_data

def generate_room_conditions(room_id: str) -> Dict[str, Any]:
    """Generate kondisi lingkungan yang bervariasi per room"""
    
    # Variasi suhu berdasarkan lokasi room dan floor
    base_temp = 22.0
    temp_variation = 0.0
    
    # Floor variation (lantai atas lebih hangat)
    floor_num = int(room_id[1]) if room_id[1].isdigit() else 2
    temp_variation += (floor_num - 2) * 0.5  # +0.5°C per lantai
    
    # Building variation (gedung G sedikit lebih dingin karena struktur)
    if room_id.startswith('G'):
        temp_variation -= 0.3
    
    # Room specific micro-variations
    room_hash = hash(room_id) % 20
    temp_variation += (room_hash - 10) * 0.1  # ±1°C variation
    
    # Humidity variation
    base_humidity = 50.0
    humidity_variation = (room_hash % 15) - 7  # ±7% variation
    
    # Time-based variation (simulate daily cycle)
    hour = datetime.now().hour
    daily_temp_cycle = 2 * math.sin((hour - 6) * math.pi / 12)  # Peak at 2 PM
    
    # Small random variation for realism
    import random
    random.seed(room_id + str(hour))  # Consistent but varying seed
    temp_noise = random.uniform(-0.2, 0.2)
    humidity_noise = random.uniform(-2, 2)
    
    return {
        "temperature": round(base_temp + temp_variation + daily_temp_cycle + temp_noise, 1),
        "humidity": round(base_humidity + humidity_variation + humidity_noise, 1),
        "co2": 400 + (room_hash % 100),  # 400-500 ppm
        "light": 350 + (room_hash % 150),  # 350-500 lux
        "air_quality": 85 + (room_hash % 15)  # 85-100 AQI
    }

def generate_daily_averages(room_id: str, current_conditions: Dict) -> Dict[str, float]:
    """Generate rata-rata harian berdasarkan kondisi saat ini"""
    return {
        "temperature": round(current_conditions["temperature"] - 0.5, 1),
        "humidity": round(current_conditions["humidity"] + 2.0, 1)
    }

def generate_optimal_time_percentages(room_id: str) -> Dict[str, int]:
    """Generate persentase waktu dalam rentang optimal"""
    room_hash = hash(room_id) % 100
    return {
        "temperature": 75 + (room_hash % 20),  # 75-95%
        "humidity": 65 + (room_hash % 25)      # 65-90%
    }

async def get_room_devices(room_id: str) -> List[Dict[str, Any]]:
    """
    Generate data perangkat yang bervariasi per room.
    
    Args:
        room_id (str): ID ruangan (contoh: F2, G3, dsb)
        
    Returns:
        List[Dict[str, Any]]: Daftar perangkat di ruangan tersebut
    """
    try:
        logger.info(f"Menggenerate data perangkat simulasi untuk ruangan {room_id}")
        
        devices = []
        
        # Buat variasi status perangkat berdasarkan room_id
        room_hash = hash(room_id) % 100
        
        # AC status - aktif untuk sebagian besar room
        ac_status = "active" if room_hash % 3 != 0 else "inactive"
        devices.append({
            "id": f"ac-{room_id.lower()}",
            "name": "AC",
            "type": "AC",
            "status": ac_status,
            "setPoint": 21 + (room_hash % 5)  # 21-25°C
        })
        
        # Dehumidifier status - bervariasi
        dh_status = "active" if room_hash % 4 != 0 else "inactive"
        devices.append({
            "id": f"dh-{room_id.lower()}",
            "name": "Dehumidifier", 
            "type": "Dehumidifier",
            "status": dh_status,
            "setPoint": 45 + (room_hash % 15)  # 45-60%
        })
        
        # Fan/Air Purifier
        fan_status = "active" if room_hash % 5 != 0 else "inactive"
        devices.append({
            "id": f"fan-{room_id.lower()}",
            "name": "Air Purifier",
            "type": "Fan", 
            "status": fan_status,
            "setPoint": None
        })
        
        return devices
        
    except Exception as e:
        logger.error(f"Error saat mengambil data perangkat untuk ruangan {room_id}: {str(e)}")
        # Return fallback data jika terjadi error
        return [
            {
                "id": f"ac-{room_id.lower()}",
                "name": "AC",
                "type": "AC",
                "status": "active",
                "setPoint": 21
            },
            {
                "id": f"dh-{room_id.lower()}",
                "name": "Dehumidifier",
                "type": "Dehumidifier", 
                "status": "active",
                "setPoint": 50
            }
        ]

async def get_room_list() -> List[Dict[str, Any]]:
    """
    Mendapatkan daftar semua ruangan yang tersedia.
    
    Returns:
        List[Dict[str, Any]]: Daftar ruangan dengan metadata dasar
    """
    rooms = []
    
    for room_id, metadata in ROOM_METADATA.items():
        rooms.append({
            "id": room_id,
            "name": metadata["name"],
            "floor": metadata["floor"],
            "area": metadata["area"]
        })
    
    return rooms
