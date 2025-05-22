"""
Contoh penggunaan arsitektur modular untuk endpoint API
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime
from typing import Dict, List, Any, Optional

from .services import execute_query
from .flux_queries import get_average_temperature_last_hour_query

# Asumsikan variabel konstan ini telah didefinisikan di tempat lain
INFLUXDB_BUCKET = "sensor_data_primary"

# Fungsi autentikasi
async def get_api_key(api_key: str = Query(...)):
    # Implementasi autentikasi
    pass

router = APIRouter()

@router.get("/stats/temperature/last-hour/", summary="Dapatkan suhu rata-rata seluruh perangkat pada jam terakhir", response_model=Dict[str, Any])
async def get_average_temperature_last_hour(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil suhu rata-rata dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    # Dapatkan query dari modul flux_queries
    flux_query = get_average_temperature_last_hour_query(INFLUXDB_BUCKET)
    
    # Gunakan service untuk mengeksekusi query
    results = await execute_query(
        query=flux_query,
        description="query suhu rata-rata 1 jam terakhir"
    )
    
    if not results or len(results) == 0 or len(results[0].records) == 0:
        return {
            "avg_temperature": None,
            "timestamp": datetime.now().isoformat()
        }
    
    # Ambil hasil agregasi
    record = results[0].records[0]
    avg_temp = round(record.get_value(), 1)
    
    return {
        "avg_temperature": avg_temp,
        "timestamp": datetime.now().isoformat()
    }
