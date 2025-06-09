# routes/recommendations_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime

# Import get_api_key dari api.py daripada mendefinisikan ulang di sini
from api import get_api_key

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/proactive")
async def get_proactive_recommendations(api_key: str = Depends(get_api_key)):
    """
    Mengambil rekomendasi proaktif berdasarkan analisis data sensor
    """
    try:
        recommendations = {
            "priority_recommendations": [
                {
                    "id": "rec_001",
                    "priority": "high",
                    "category": "temperature_control",
                    "title": "Penyesuaian Suhu Ruang F2", 
                    "description": "Suhu ruang F2 konsisten di atas target. Disarankan menurunkan setpoint AC 1-2°C",
                    "action": "adjust_hvac",
                    "room": "F2",
                    "estimated_impact": "Penurunan suhu rata-rata 2°C dalam 30 menit",
                    "energy_saving": "5-8% penghematan energi",
                    "created_at": "2025-06-03T21:30:00"
                },
                {
                    "id": "rec_002", 
                    "priority": "medium",
                    "category": "humidity_control",
                    "title": "Optimasi Kelembapan",
                    "description": "Kelembapan beberapa ruangan mendekati batas atas. Pertimbangkan penyesuaian dehumidifier",
                    "action": "adjust_dehumidifier", 
                    "room": "G3,G4",
                    "estimated_impact": "Penurunan kelembapan 5-10%",
                    "energy_saving": "3-5% penghematan energi",
                    "created_at": "2025-06-03T21:15:00"
                }
            ],
            "general_recommendations": [
                {
                    "id": "rec_003",
                    "priority": "low", 
                    "category": "maintenance",
                    "title": "Kalibrasi Sensor Berkala",
                    "description": "Lakukan kalibrasi sensor suhu dan kelembapan setiap 3 bulan",
                    "action": "schedule_maintenance",
                    "next_due": "2025-07-01",
                    "created_at": "2025-06-03T20:00:00"
                }
            ],
            "total_recommendations": 3,
            "last_updated": datetime.now().isoformat(),
            "analysis_period": "last_24_hours"
        }
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")
