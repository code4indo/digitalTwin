# routes/alert_routes.py
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import get_api_key dari api.py daripada mendefinisikan ulang di sini
from utils.auth import get_api_key

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/")
async def get_alerts(
    filter: Optional[str] = Query("all", description="Filter untuk jenis alert"),
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil daftar alert sistem
    """
    try:
        # Untuk sementara, return data dummy
        # Nanti bisa diintegrasikan dengan sistem monitoring real
        alerts = [
            {
                "id": "alert_001",
                "type": "warning",
                "title": "Suhu Tinggi Terdeteksi",
                "message": "Suhu di ruang F2 mencapai 28.5°C, di atas batas normal 27°C",
                "room": "F2",
                "parameter": "temperature",
                "value": 28.5,
                "threshold": 27.0,
                "timestamp": "2025-06-03T22:00:00",
                "status": "active",
                "severity": "medium"
            },
            {
                "id": "alert_002", 
                "type": "info",
                "title": "Kelembapan Optimal",
                "message": "Semua ruangan memiliki kelembapan dalam rentang optimal",
                "room": "all",
                "parameter": "humidity", 
                "timestamp": "2025-06-03T21:30:00",
                "status": "resolved",
                "severity": "low"
            }
        ]
        
        # Filter berdasarkan parameter filter jika diperlukan
        if filter != "all":
            alerts = [alert for alert in alerts if alert.get("type") == filter]
            
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "filter_applied": filter,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")
