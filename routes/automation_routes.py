# routes/automation_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime

# Import get_api_key dari api.py daripada mendefinisikan ulang di sini
from utils.auth import get_api_key
from pydantic import BaseModel

router = APIRouter(prefix="/automation", tags=["automation"])

class AutomationSettings(BaseModel):
    temperature_control: bool = True
    humidity_control: bool = True
    target_temperature: float = 24.0
    target_humidity: float = 60.0
    auto_alerts: bool = True
    alert_threshold_temp: float = 27.0
    alert_threshold_humidity: float = 75.0

@router.get("/settings")
async def get_automation_settings(api_key: str = Depends(get_api_key)):
    """
    Mengambil pengaturan otomasi saat ini
    """
    try:
        # Return default settings
        settings = {
            "temperature_control": True,
            "humidity_control": True,
            "target_temperature": 24.0,
            "temperature_tolerance": 2.0,
            "target_humidity": 60.0,
            "humidity_tolerance": 10.0,
            "auto_alerts": True,
            "alert_threshold_temp": 27.0,
            "alert_threshold_humidity": 75.0,
            "schedule_enabled": True,
            "schedule": {
                "weekdays": {
                    "start_time": "07:00",
                    "end_time": "18:00",
                    "target_temp": 24.0
                },
                "weekends": {
                    "start_time": "09:00", 
                    "end_time": "17:00",
                    "target_temp": 25.0
                }
            },
            "last_updated": "2025-06-03T20:00:00",
            "updated_by": "admin"
        }
        
        return settings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching automation settings: {str(e)}")

@router.put("/settings")
async def update_automation_settings(
    settings: AutomationSettings,
    api_key: str = Depends(get_api_key)
):
    """
    Memperbarui pengaturan otomasi
    """
    try:
        # Simulate updating settings
        updated_settings = {
            **settings.dict(),
            "last_updated": datetime.now().isoformat(),
            "updated_by": "admin"
        }
        
        return {
            "message": "Automation settings updated successfully",
            "settings": updated_settings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating automation settings: {str(e)}")
