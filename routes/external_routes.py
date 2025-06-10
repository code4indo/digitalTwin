# routes/external_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime
import requests

# Import get_api_key dari api.py 
from utils.auth import get_api_key

router = APIRouter(prefix="/external", tags=["external"])

@router.get("/bmkg/latest")
async def get_latest_bmkg_data(api_key: str = Depends(get_api_key)):
    """
    Mengambil data cuaca terbaru langsung dari API BMKG
    """
    try:
        # Konfigurasi API BMKG
        BMKG_API_URL = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
        KODE_WILAYAH = "31.74.04.1003"  # Cilandak Timur, Jakarta Selatan
        
        # Fetch data dari API BMKG
        bmkg_response = requests.get(
            f"{BMKG_API_URL}?adm4={KODE_WILAYAH}",
            timeout=15
        )
        
        if bmkg_response.status_code == 200:
            raw_data = bmkg_response.json()
            
            # Extract data cuaca terkini
            if "data" in raw_data and len(raw_data["data"]) > 0:
                data_entry = raw_data["data"][0]
                location_info = data_entry.get("lokasi", {})
                cuaca_days = data_entry.get("cuaca", [])
                
                # Ambil forecast terkini (jam terdekat)
                current_forecast = None
                if cuaca_days and len(cuaca_days[0]) > 0:
                    current_forecast = cuaca_days[0][0]  # Forecast pertama hari ini
                
                if current_forecast:
                    # Map data BMKG ke format response
                    bmkg_data = {
                        "weather_data": {
                            "temperature": current_forecast.get("t"),
                            "humidity": current_forecast.get("hu"),
                            "wind_speed": current_forecast.get("ws"),
                            "wind_direction": current_forecast.get("wd_to", "N/A"),
                            "pressure": None,  # BMKG API tidak menyediakan pressure
                            "visibility": current_forecast.get("vs_text", "").replace("> ", "").replace(" km", "") or None,
                            "weather_condition": current_forecast.get("weather_desc", ""),
                            "weather_code": current_forecast.get("weather", "")
                        },
                        "location": {
                            "region": location_info.get("provinsi", "DKI Jakarta"),
                            "station": location_info.get("kecamatan", "Pasar Minggu"),
                            "coordinates": {
                                "latitude": location_info.get("lat"),
                                "longitude": location_info.get("lon")
                            }
                        },
                        "timestamp": datetime.now().isoformat(),
                        "data_source": "BMKG API Real-time",
                        "last_updated": current_forecast.get("utc_datetime", datetime.now().isoformat()),
                        "forecast_details": {
                            "local_time": current_forecast.get("local_datetime", ""),
                            "weather_desc_en": current_forecast.get("weather_desc_en", ""),
                            "analysis_date": current_forecast.get("analysis_date", "")
                        }
                    }
                    
                    return bmkg_data
                    
        # Fallback jika gagal
        raise Exception("Failed to get valid data from BMKG API")
        
    except Exception as e:
        print(f"Error fetching real BMKG data: {str(e)}")
        # Return fallback data dengan indikasi error
        return {
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
                "region": "DKI Jakarta",
                "station": "Cilandak Timur",
                "coordinates": {
                    "latitude": -6.2912471594,
                    "longitude": 106.8127643945
                }
            },
            "timestamp": datetime.now().isoformat(),
            "data_source": "BMKG (Fallback - API Error)",
            "last_updated": datetime.now().isoformat(),
            "error": str(e),
            "note": "Using fallback data due to BMKG API connectivity issues"
        }
