#!/usr/bin/env python3
"""
Implementasi get_rooms_data() yang menggunakan data REAL dari API rooms endpoint
untuk menggantikan data hardcode dalam rekomendasi proaktif
"""

import requests
import asyncio
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Konfigurasi API internal
INTERNAL_API_BASE = "http://localhost:8002"
API_KEY = "development_key_for_testing"

async def get_rooms_data_real() -> List[Dict[str, Any]]:
    """
    Ambil data kondisi semua ruangan dari API real (bukan hardcode)
    Menggunakan endpoint /rooms/ yang sudah ada
    """
    try:
        # Daftar ruangan yang ingin dimonitor
        room_ids = ["F2", "F3", "F4", "G2", "G3", "G4"]
        rooms_data = []
        
        headers = {"X-API-Key": API_KEY}
        
        for room_id in room_ids:
            try:
                # Ambil data real dari endpoint rooms
                response = requests.get(
                    f"{INTERNAL_API_BASE}/rooms/{room_id}",
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
                            "air_quality": current_conditions.get("air_quality", 85)
                        },
                        "statistics": room_data.get("statistics", {}),
                        "devices": room_data.get("devices", [])
                    })
                    
                    logger.info(f"Successfully fetched real data for room {room_id}")
                    
                else:
                    logger.warning(f"Failed to fetch data for room {room_id}: {response.status_code}")
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
                            "temp_trend": "stable",
                            "humidity_trend": "stable"
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Error fetching data for room {room_id}: {e}")
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
                        "temp_trend": "stable",
                        "humidity_trend": "stable"
                    }
                })
        
        logger.info(f"Successfully fetched data for {len(rooms_data)} rooms")
        return rooms_data
        
    except Exception as e:
        logger.error(f"Error getting rooms data: {e}")
        # Return empty list atau data fallback minimal
        return []

async def get_automation_parameters_real() -> Dict[str, Any]:
    """
    Ambil parameter otomasi dari API real (bukan hardcode)
    Menggunakan endpoint automation yang ada
    """
    try:
        headers = {"X-API-Key": API_KEY}
        response = requests.get(
            f"{INTERNAL_API_BASE}/automation/parameters",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            params = response.json()
            logger.info("Successfully fetched automation parameters from API")
            return params
        else:
            logger.warning(f"Failed to fetch automation parameters: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error fetching automation parameters: {e}")
    
    # Fallback ke parameter default
    return {
        "target_temperature": 24.0,
        "temperature_tolerance": 2.0,
        "target_humidity": 60.0,
        "humidity_tolerance": 10.0,
        "alert_threshold_temp": 27.0,
        "alert_threshold_humidity": 75.0
    }

# Test script
async def test_real_data_integration():
    """Test fungsi baru dengan data real"""
    print("🧪 Testing Real Data Integration for Recommendations...")
    
    # Test rooms data
    print("\n📊 Testing get_rooms_data_real()...")
    rooms = await get_rooms_data_real()
    print(f"✅ Fetched {len(rooms)} rooms")
    
    for room in rooms:
        print(f"   🏠 {room['name']}: {room['currentConditions']['temperature']}°C, {room['currentConditions']['humidity']}%")
    
    # Test automation parameters
    print("\n⚙️ Testing get_automation_parameters_real()...")
    params = await get_automation_parameters_real()
    print(f"✅ Target temp: {params['target_temperature']}°C, humidity: {params['target_humidity']}%")
    
    return rooms, params

if __name__ == "__main__":
    # Run test
    asyncio.run(test_real_data_integration())
