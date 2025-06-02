"""
Service untuk mengelola data ruangan dalam aplikasi Digital Twin.
"""

import logging
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional, Any
from influxdb_client import InfluxDBClient
from flux_queries.room_data import get_room_environmental_data, get_room_device_status
import os

# Konfigurasi logging
logger = logging.getLogger(__name__)

# Konfigurasi InfluxDB dari environment variables
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "iot_project_alpha")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET_PRIMARY", "sensor_data_primary")

# Buat koneksi ke InfluxDB
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = influx_client.query_api()

# Konstanta untuk room metadata
# Dalam implementasi produksi, ini bisa berasal dari database
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
    Mengambil data detail ruangan, termasuk kondisi lingkungan terkini
    dan informasi perangkat.
    
    Args:
        room_id (str): ID ruangan (contoh: F2, G3, dsb)
        
    Returns:
        Dict[str, Any]: Data ruangan dengan format JSON
    """
    logger.info(f"Mengambil detail ruangan untuk {room_id}")
    
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
        # Ambil data lingkungan ruangan dari InfluxDB
        query = get_room_environmental_data(room_id)
        result = query_api.query(query, org=INFLUXDB_ORG)
        
        # Extract data-data yang diperlukan
        current_conditions = {}
        daily_avg = {}
        time_in_optimal_range = {}
        
        # Cek apakah data ada
        if result:
            for table in result:
                # Proses data berdasarkan nama result
                if table.records and table.name == "current_conditions":
                    record = table.records[0]
                    
                    # Ambil nilai suhu dan kelembapan jika ada
                    if hasattr(record, 'values') and 'temperature' in record.values:
                        current_conditions["temperature"] = round(float(record.values["temperature"]), 1)
                    if hasattr(record, 'values') and 'humidity' in record.values:
                        current_conditions["humidity"] = round(float(record.values["humidity"]), 1)
                
                # Proses rata-rata harian
                elif table.records and table.name == "daily_averages":
                    record = table.records[0]
                    if hasattr(record, 'values'):
                        if 'daily_avg_temperature' in record.values:
                            daily_avg["temperature"] = round(float(record.values["daily_avg_temperature"]), 1)
                        if 'daily_avg_humidity' in record.values:
                            daily_avg["humidity"] = round(float(record.values["daily_avg_humidity"]), 1)
                
                # Proses faktor lingkungan tambahan
                elif table.records and table.name == "environmental_factors":
                    record = table.records[0]
                    if hasattr(record, 'values'):
                        if 'co2' in record.values:
                            current_conditions["co2"] = int(record.values["co2"])
                        if 'light' in record.values:
                            current_conditions["light"] = int(record.values["light"])
                
                # Proses persentase waktu dalam rentang optimal
                elif table.records and table.name == "optimal_temp_percentage":
                    record = table.records[0]
                    if hasattr(record, 'values') and 'optimal_temp_percentage' in record.values:
                        time_in_optimal_range["temperature"] = int(record.values["optimal_temp_percentage"])
                
                elif table.records and table.name == "optimal_humidity_percentage":
                    record = table.records[0]
                    if hasattr(record, 'values') and 'optimal_humidity_percentage' in record.values:
                        time_in_optimal_range["humidity"] = int(record.values["optimal_humidity_percentage"])
        
        # Berikan nilai default jika data tidak tersedia
        if not current_conditions:
            current_conditions = {
                "temperature": 22.5,
                "humidity": 50.0,
                "co2": 450,
                "light": 400
            }
        
        if not daily_avg:
            daily_avg = {
                "temperature": 22.0,
                "humidity": 48.0
            }
            
        if not time_in_optimal_range:
            time_in_optimal_range = {
                "temperature": 85,
                "humidity": 70
            }
        
        # Ambil data perangkat terkini
        devices = await get_room_devices(room_id)
        
        # Buat struktur data lengkap
        room_data.update({
            "currentConditions": current_conditions,
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


async def get_room_devices(room_id: str) -> List[Dict[str, Any]]:
    """
    Mengambil data perangkat untuk ruangan tertentu.
    
    Args:
        room_id (str): ID ruangan (contoh: F2, G3, dsb)
        
    Returns:
        List[Dict[str, Any]]: Daftar perangkat di ruangan tersebut
    """
    try:
        # Query InfluxDB untuk status perangkat
        query = get_room_device_status(room_id)
        result = query_api.query(query, org=INFLUXDB_ORG)
        
        devices = []
        
        # Cek apakah data ada
        ac_data = None
        dehumidifier_data = None
        
        if result:
            for table in result:
                # Proses data berdasarkan nama result
                if table.records and table.name == "ac_status":
                    if table.records:
                        record = table.records[0]
                        if hasattr(record, 'values'):
                            ac_data = {
                                "id": f"ac-{room_id.lower()}",
                                "name": "AC",
                                "status": "active" if record.values.get("status", "0") == "1" else "inactive",
                                "setPoint": float(record.values.get("set_point", 21))
                            }
                
                # Proses data dehumidifier
                elif table.records and table.name == "dehumidifier_status":
                    if table.records:
                        record = table.records[0]
                        if hasattr(record, 'values'):
                            dehumidifier_data = {
                                "id": f"dh-{room_id.lower()}",
                                "name": "Dehumidifier",
                                "status": "active" if record.values.get("status", "0") == "1" else "inactive",
                                "setPoint": float(record.values.get("set_point", 50))
                            }
        
        # Tambahkan data perangkat jika ditemukan
        if ac_data:
            devices.append(ac_data)
        else:
            # Fallback data jika tidak ada
            devices.append({
                "id": f"ac-{room_id.lower()}",
                "name": "AC",
                "status": "active",
                "setPoint": 21
            })
            
        if dehumidifier_data:
            devices.append(dehumidifier_data)
        else:
            # Fallback data jika tidak ada
            devices.append({
                "id": f"dh-{room_id.lower()}",
                "name": "Dehumidifier",
                "status": "active",
                "setPoint": 50
            })
            
        return devices
        
    except Exception as e:
        logger.error(f"Error saat mengambil data perangkat untuk ruangan {room_id}: {str(e)}")
        # Return fallback data jika terjadi error
        return [
            {
                "id": f"ac-{room_id.lower()}",
                "name": "AC",
                "status": "active",
                "setPoint": 21
            },
            {
                "id": f"dh-{room_id.lower()}",
                "name": "Dehumidifier",
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
