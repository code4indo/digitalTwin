#!/usr/bin/env python3
"""
Enhanced API endpoints untuk mendukung visualisasi digital twin yang lebih informatif.
Menambahkan endpoint untuk data ruangan real-time dengan informasi device dan sensor.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional, Any
import random
from datetime import datetime, timedelta
import asyncio

# Router untuk enhanced endpoints
enhanced_router = APIRouter(prefix="/enhanced", tags=["enhanced"])

def generate_room_conditions(room_id: str) -> Dict[str, Any]:
    """Generate realistic room environmental conditions"""
    
    # Base values with some variation by room
    room_base_temps = {
        'F2': 22.0, 'F3': 21.5, 'F4': 22.5, 'F5': 21.8, 'F6': 22.2,
        'G2': 23.0, 'G3': 22.8, 'G4': 23.2, 'G5': 22.5, 'G6': 23.1, 'G7': 22.9, 'G8': 23.3
    }
    
    room_base_humidity = {
        'F2': 48.0, 'F3': 50.0, 'F4': 47.0, 'F5': 49.0, 'F6': 48.5,
        'G2': 52.0, 'G3': 51.0, 'G4': 53.0, 'G5': 50.5, 'G6': 52.5, 'G7': 51.8, 'G8': 53.2
    }
    
    base_temp = room_base_temps.get(room_id, 22.0)
    base_humidity = room_base_humidity.get(room_id, 50.0)
    
    # Add some realistic variation
    current_temp = base_temp + random.uniform(-1.5, 1.5)
    current_humidity = base_humidity + random.uniform(-5, 5)
    
    # Ensure values are within reasonable ranges
    current_temp = max(18, min(26, current_temp))
    current_humidity = max(35, min(65, current_humidity))
    
    return {
        "temperature": round(current_temp, 1),
        "humidity": round(current_humidity, 1),
        "co2": round(400 + random.uniform(0, 300), 0),
        "light": round(300 + random.uniform(0, 400), 0),
        "air_pressure": round(1013.25 + random.uniform(-5, 5), 2)
    }

def generate_device_status(room_id: str) -> List[Dict[str, Any]]:
    """Generate device status for a room"""
    
    devices = [
        {
            "id": f"ac-{room_id.lower()}",
            "name": "Air Conditioner",
            "type": "hvac",
            "status": "active" if random.random() > 0.1 else "inactive",
            "setPoint": random.randint(19, 23),
            "currentOutput": round(random.uniform(30, 85), 1),
            "energyConsumption": round(random.uniform(1.2, 3.5), 2),
            "lastMaintenance": (datetime.now() - timedelta(days=random.randint(10, 90))).isoformat()
        },
        {
            "id": f"dh-{room_id.lower()}",
            "name": "Dehumidifier", 
            "type": "humidity_control",
            "status": "active" if random.random() > 0.15 else "inactive",
            "setPoint": random.randint(45, 55),
            "currentOutput": round(random.uniform(20, 70), 1),
            "energyConsumption": round(random.uniform(0.8, 2.1), 2),
            "lastMaintenance": (datetime.now() - timedelta(days=random.randint(5, 60))).isoformat()
        },
        {
            "id": f"fan-{room_id.lower()}",
            "name": "Circulation Fan",
            "type": "ventilation",
            "status": "active" if random.random() > 0.2 else "inactive", 
            "setPoint": random.randint(1, 5),  # Speed level
            "currentOutput": round(random.uniform(10, 90), 1),
            "energyConsumption": round(random.uniform(0.1, 0.8), 2),
            "lastMaintenance": (datetime.now() - timedelta(days=random.randint(15, 120))).isoformat()
        }
    ]
    
    return devices

def generate_sensor_status(room_id: str) -> Dict[str, Any]:
    """Generate sensor status for a room"""
    
    return {
        "id": f"sensor-{room_id.lower()}",
        "status": "active" if random.random() > 0.05 else "offline",
        "batteryLevel": random.randint(15, 100),
        "signalStrength": random.randint(60, 95),
        "lastReading": datetime.now().isoformat(),
        "calibrationDate": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
        "accuracy": round(random.uniform(95, 99.5), 1)
    }

def calculate_room_health_score(conditions: Dict, devices: List[Dict], sensor: Dict) -> Dict[str, Any]:
    """Calculate overall health score for a room"""
    
    # Temperature score (optimal: 18-24°C)
    temp = conditions["temperature"]
    if 18 <= temp <= 24:
        temp_score = 100
    elif 16 <= temp <= 26:
        temp_score = 80
    else:
        temp_score = 50
    
    # Humidity score (optimal: 40-60%)
    humidity = conditions["humidity"]
    if 40 <= humidity <= 60:
        humidity_score = 100
    elif 35 <= humidity <= 65:
        humidity_score = 80
    else:
        humidity_score = 50
    
    # Device score
    active_devices = sum(1 for d in devices if d["status"] == "active")
    device_score = (active_devices / len(devices)) * 100
    
    # Sensor score
    sensor_score = 100 if sensor["status"] == "active" else 0
    
    # Overall score
    overall_score = (temp_score * 0.3 + humidity_score * 0.3 + device_score * 0.3 + sensor_score * 0.1)
    
    if overall_score >= 90:
        status = "optimal"
    elif overall_score >= 75:
        status = "good"
    elif overall_score >= 60:
        status = "warning"
    else:
        status = "critical"
    
    return {
        "overallScore": round(overall_score, 1),
        "status": status,
        "scores": {
            "temperature": temp_score,
            "humidity": humidity_score,
            "devices": round(device_score, 1),
            "sensor": sensor_score
        }
    }

@enhanced_router.get("/rooms/{room_id}/environmental")
async def get_enhanced_room_data(room_id: str):
    """
    Get comprehensive environmental data for a specific room including:
    - Current conditions (temperature, humidity, CO2, light)
    - Device status and performance
    - Sensor status and health
    - Room health score
    """
    
    # Validate room ID
    valid_rooms = ['F2', 'F3', 'F4', 'F5', 'F6', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8']
    if room_id not in valid_rooms:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    
    # Generate data
    conditions = generate_room_conditions(room_id)
    devices = generate_device_status(room_id)
    sensor = generate_sensor_status(room_id)
    health = calculate_room_health_score(conditions, devices, sensor)
    
    return {
        "id": room_id,
        "name": f"Room {room_id}",
        "floor": room_id[0],
        "area": random.randint(20, 40),  # Square meters
        "currentConditions": conditions,
        "devices": devices,
        "sensorStatus": sensor,
        "healthScore": health,
        "lastUpdate": datetime.now().isoformat(),
        "operatingMode": random.choice(["normal", "energy_saving", "high_performance"]),
        "targetConditions": {
            "temperature": random.randint(20, 22),
            "humidity": random.randint(45, 55)
        }
    }

@enhanced_router.get("/rooms/overview")
async def get_all_rooms_overview():
    """
    Get overview data for all rooms - useful for heat map visualization
    """
    
    valid_rooms = ['F2', 'F3', 'F4', 'F5', 'F6', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8']
    rooms_data = {}
    
    for room_id in valid_rooms:
        conditions = generate_room_conditions(room_id)
        devices = generate_device_status(room_id)
        sensor = generate_sensor_status(room_id)
        health = calculate_room_health_score(conditions, devices, sensor)
        
        rooms_data[room_id] = {
            "id": room_id,
            "currentConditions": conditions,
            "deviceCount": {
                "total": len(devices),
                "active": sum(1 for d in devices if d["status"] == "active")
            },
            "sensorStatus": sensor["status"],
            "healthScore": health,
            "lastUpdate": datetime.now().isoformat()
        }
    
    return {
        "timestamp": datetime.now().isoformat(),
        "totalRooms": len(valid_rooms),
        "rooms": rooms_data
    }

@enhanced_router.get("/system/building-overview")
async def get_building_overview():
    """
    Get building-wide overview including floor statistics
    """
    
    rooms_data = await get_all_rooms_overview()
    rooms = rooms_data["rooms"]
    
    # Calculate floor statistics
    floor_f_rooms = [r for r in rooms.values() if r["id"].startswith("F")]
    floor_g_rooms = [r for r in rooms.values() if r["id"].startswith("G")]
    
    def calculate_floor_stats(floor_rooms):
        if not floor_rooms:
            return {"avgTemp": 0, "avgHumidity": 0, "activeDevices": 0, "totalDevices": 0}
            
        avg_temp = sum(r["currentConditions"]["temperature"] for r in floor_rooms) / len(floor_rooms)
        avg_humidity = sum(r["currentConditions"]["humidity"] for r in floor_rooms) / len(floor_rooms)
        active_devices = sum(r["deviceCount"]["active"] for r in floor_rooms)
        total_devices = sum(r["deviceCount"]["total"] for r in floor_rooms)
        
        return {
            "avgTemp": round(avg_temp, 1),
            "avgHumidity": round(avg_humidity, 1),
            "activeDevices": active_devices,
            "totalDevices": total_devices,
            "deviceEfficiency": round((active_devices / total_devices) * 100, 1) if total_devices > 0 else 0
        }
    
    # Calculate overall building stats
    all_temps = [r["currentConditions"]["temperature"] for r in rooms.values()]
    all_humidity = [r["currentConditions"]["humidity"] for r in rooms.values()]
    all_scores = [r["healthScore"]["overallScore"] for r in rooms.values()]
    
    critical_rooms = [r["id"] for r in rooms.values() if r["healthScore"]["status"] == "critical"]
    warning_rooms = [r["id"] for r in rooms.values() if r["healthScore"]["status"] == "warning"]
    optimal_rooms = [r["id"] for r in rooms.values() if r["healthScore"]["status"] == "optimal"]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "buildingStats": {
            "totalRooms": len(rooms),
            "avgTemperature": round(sum(all_temps) / len(all_temps), 1),
            "avgHumidity": round(sum(all_humidity) / len(all_humidity), 1),
            "avgHealthScore": round(sum(all_scores) / len(all_scores), 1),
            "temperatureRange": {
                "min": round(min(all_temps), 1),
                "max": round(max(all_temps), 1)
            },
            "humidityRange": {
                "min": round(min(all_humidity), 1),
                "max": round(max(all_humidity), 1)
            }
        },
        "floorStats": {
            "F": calculate_floor_stats(floor_f_rooms),
            "G": calculate_floor_stats(floor_g_rooms)
        },
        "alertSummary": {
            "critical": len(critical_rooms),
            "warning": len(warning_rooms),
            "optimal": len(optimal_rooms),
            "criticalRooms": critical_rooms,
            "warningRooms": warning_rooms
        },
        "rooms": rooms
    }

@enhanced_router.get("/predictions/{room_id}")
async def get_room_predictions(
    room_id: str,
    hours: int = Query(default=1, ge=1, le=24, description="Hours ahead to predict")
):
    """
    Get environmental predictions for a specific room
    """
    
    valid_rooms = ['F2', 'F3', 'F4', 'F5', 'F6', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8']
    if room_id not in valid_rooms:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    
    # Get current conditions
    current_data = await get_enhanced_room_data(room_id)
    current_temp = current_data["currentConditions"]["temperature"]
    current_humidity = current_data["currentConditions"]["humidity"]
    
    predictions = []
    
    for hour in range(1, hours + 1):
        # Simple prediction with trend and some randomness
        temp_trend = random.uniform(-0.2, 0.2) * hour
        humidity_trend = random.uniform(-0.5, 0.5) * hour
        
        predicted_temp = current_temp + temp_trend + random.uniform(-0.5, 0.5)
        predicted_humidity = current_humidity + humidity_trend + random.uniform(-1, 1)
        
        # Keep within reasonable bounds
        predicted_temp = max(18, min(26, predicted_temp))
        predicted_humidity = max(35, min(65, predicted_humidity))
        
        predictions.append({
            "timestamp": (datetime.now() + timedelta(hours=hour)).isoformat(),
            "hoursAhead": hour,
            "temperature": round(predicted_temp, 1),
            "humidity": round(predicted_humidity, 1),
            "confidence": round(max(50, 95 - hour * 3), 1)  # Confidence decreases over time
        })
    
    return {
        "roomId": room_id,
        "currentConditions": current_data["currentConditions"],
        "predictions": predictions,
        "generatedAt": datetime.now().isoformat()
    }

# Export untuk diintegrasikan dengan main API
def get_enhanced_router():
    """Return the enhanced router for integration with main API"""
    return enhanced_router

if __name__ == "__main__":
    print("Enhanced API endpoints untuk Digital Twin")
    print("Endpoints yang tersedia:")
    print("- GET /enhanced/rooms/{room_id}/environmental")
    print("- GET /enhanced/rooms/overview") 
    print("- GET /enhanced/system/building-overview")
    print("- GET /enhanced/predictions/{room_id}")
