"""
Contoh API endpoint yang menggunakan pendekatan modular.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime
from typing import Dict, List, Any, Optional

# Impor service yang telah dimodularisasi
from services.stats_service import (
    get_average_temperature_last_hour,
    get_temperature_stats,
    get_humidity_stats,
    get_environmental_stats,
    get_average_humidity_last_hour,
    get_min_humidity_last_hour,
    get_max_humidity_last_hour,
    get_humidity_stats_last_hour,
    get_temperature_stats_last_hour
)

# Import get_api_key dari api.py daripada mendefinisikan ulang di sini
from api import get_api_key

router = APIRouter(prefix="/stats", tags=["statistics"])

@router.get("/temperature/last-hour/", summary="Dapatkan suhu rata-rata seluruh perangkat pada jam terakhir", 
            response_model=Dict[str, Any])
async def get_avg_temp_last_hour_endpoint(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil suhu rata-rata dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    return await get_average_temperature_last_hour()


@router.get("/temperature/", summary="Dapatkan statistik suhu dari seluruh perangkat", 
            response_model=Dict[str, Any])
async def get_temp_stats_endpoint(
    start_time: Optional[datetime] = Query(None, description="Waktu mulai (format ISO, cth: 2023-01-01T00:00:00Z). Default: 24 jam terakhir."),
    end_time: Optional[datetime] = Query(None, description="Waktu selesai (format ISO, cth: 2023-01-01T01:00:00Z). Default: sekarang."),
    locations: Optional[List[str]] = Query(None, description="Daftar lokasi untuk difilter"),
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil statistik suhu (rata-rata, minimum, maksimum) dari seluruh perangkat yang dimonitor.
    Data dapat difilter berdasarkan rentang waktu dan lokasi.
    Memerlukan autentikasi API Key.
    """
    return await get_temperature_stats(start_time, end_time, locations)


@router.get("/humidity/", summary="Dapatkan statistik kelembapan dari seluruh perangkat", 
           response_model=Dict[str, Any])
async def get_humidity_stats_endpoint(
    start_time: Optional[datetime] = Query(None, description="Waktu mulai (format ISO, cth: 2023-01-01T00:00:00Z). Default: 24 jam terakhir."),
    end_time: Optional[datetime] = Query(None, description="Waktu selesai (format ISO, cth: 2023-01-01T01:00:00Z). Default: sekarang."),
    locations: Optional[List[str]] = Query(None, description="Daftar lokasi untuk difilter"),
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil statistik kelembapan (rata-rata, minimum, maksimum) dari seluruh perangkat yang dimonitor.
    Data dapat difilter berdasarkan rentang waktu dan lokasi.
    Memerlukan autentikasi API Key.
    """
    return await get_humidity_stats(start_time, end_time, locations)


@router.get("/environmental/", summary="Dapatkan statistik suhu dan kelembapan dari seluruh perangkat", 
           response_model=Dict[str, Any])
async def get_environmental_stats_endpoint(
    start_time: Optional[datetime] = Query(None, description="Waktu mulai (format ISO, cth: 2023-01-01T00:00:00Z). Default: 24 jam terakhir."),
    end_time: Optional[datetime] = Query(None, description="Waktu selesai (format ISO, cth: 2023-01-01T01:00:00Z). Default: sekarang."),
    locations: Optional[List[str]] = Query(None, description="Daftar lokasi untuk difilter"),
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil statistik suhu dan kelembapan (rata-rata, minimum, maksimum) dari seluruh perangkat yang dimonitor.
    Data dapat difilter berdasarkan rentang waktu dan lokasi.
    Memerlukan autentikasi API Key.
    """
    return await get_environmental_stats(start_time, end_time, locations)


@router.get("/humidity/last-hour/", summary="Dapatkan kelembapan rata-rata seluruh perangkat pada jam terakhir", 
            response_model=Dict[str, Any])
async def get_avg_humidity_last_hour_endpoint(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil kelembapan rata-rata dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    return await get_average_humidity_last_hour()


@router.get("/humidity/last-hour/min/", summary="Dapatkan kelembapan minimum seluruh perangkat pada jam terakhir", 
            response_model=Dict[str, Any])
async def get_min_humidity_last_hour_endpoint(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil kelembapan minimum dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    return await get_min_humidity_last_hour()


@router.get("/humidity/last-hour/max/", summary="Dapatkan kelembapan maksimum seluruh perangkat pada jam terakhir", 
            response_model=Dict[str, Any])
async def get_max_humidity_last_hour_endpoint(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil kelembapan maksimum dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    return await get_max_humidity_last_hour()


@router.get("/humidity/last-hour/stats/", summary="Dapatkan statistik kelembapan seluruh perangkat pada jam terakhir", 
            response_model=Dict[str, Any])
async def get_humidity_stats_last_hour_endpoint(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil statistik kelembapan (rata-rata, minimum, maksimum) dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    return await get_humidity_stats_last_hour()


@router.get("/temperature/last-hour/stats/", summary="Dapatkan statistik suhu seluruh perangkat pada jam terakhir", 
            response_model=Dict[str, Any])
async def get_temperature_stats_last_hour_endpoint(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil statistik suhu (rata-rata, minimum, maksimum) dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    return await get_temperature_stats_last_hour()
