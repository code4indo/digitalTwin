# routes/external_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime

# Import get_api_key dari api.py daripada mendefinisikan ulang di sini
from api import get_api_key

router = APIRouter(prefix="/external", tags=["external"])

@router.get("/bmkg/latest")
async def get_latest_bmkg_data(api_key: str = Depends(get_api_key)):
    """
    Mengambil data cuaca terbaru dari BMKG
    """
    try:
        # Untuk sementara, return data dummy
        # Nanti bisa diintegrasikan dengan data BMKG collector yang sebenarnya
        bmkg_data = {
            "weather_data": {
                "temperature": 26.5,
                "humidity": 78,
                "wind_speed": 12.3,
                "wind_direction": "SE", 
                "pressure": 1013.2,
                "visibility": 10,
                "weather_condition": "Partly Cloudy",
                "weather_code": "03d"
            },
            "location": {
                "region": "Jakarta",
                "station": "Kemayoran",
                "coordinates": {
                    "latitude": -6.1745,
                    "longitude": 106.8227
                }
            },
            "timestamp": datetime.now().isoformat(),
            "data_source": "BMKG",
            "last_updated": "2025-06-03T22:00:00"
        }
        
        return bmkg_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching BMKG data: {str(e)}")
