"""
Routes untuk analisis tren data sensor
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import service untuk analisis tren
from services.trend_service import (
    get_hourly_trend_data,
    get_daily_trend_data,
    get_monthly_trend_data,
    get_comparative_trend_analysis
)

# Import get_api_key dari api.py
from api import get_api_key

router = APIRouter(prefix="/data", tags=["trend_analysis"])

@router.get("/trends", summary="Endpoint utama untuk analisis tren", 
            response_model=Dict[str, Any])
async def get_trend_data_endpoint(
    period: str = Query("day", description="Periode analisis: 'day', 'week', atau 'month'"),
    parameter: str = Query("temperature", description="Parameter sensor: 'temperature' atau 'humidity'"),
    location: Optional[str] = Query("all", description="Lokasi spesifik atau 'all' untuk semua lokasi"),
    api_key: str = Depends(get_api_key)
):
    """
    Endpoint utama untuk mengambil data analisis tren.
    Mendukung analisis harian, mingguan, dan bulanan.
    Memerlukan autentikasi API Key.
    """
    try:
        if period == "day":
            return await get_hourly_trend_data(parameter, location, hours=24)
        elif period == "week":
            return await get_daily_trend_data(parameter, location, days=7)
        elif period == "month":
            return await get_monthly_trend_data(parameter, location, days=30)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Period '{period}' tidak didukung. Gunakan 'day', 'week', atau 'month'"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dalam analisis tren: {str(e)}")


@router.get("/trends/hourly", summary="Analisis tren per jam", 
            response_model=Dict[str, Any])
async def get_hourly_trend_endpoint(
    parameter: str = Query("temperature", description="Parameter sensor: 'temperature' atau 'humidity'"),
    location: Optional[str] = Query("all", description="Lokasi spesifik atau 'all' untuk semua lokasi"),
    hours: int = Query(24, description="Jumlah jam data yang diambil (default: 24)", ge=1, le=168),
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil analisis tren per jam untuk parameter dan lokasi tertentu.
    Mendukung data hingga 168 jam (7 hari) ke belakang.
    Memerlukan autentikasi API Key.
    """
    return await get_hourly_trend_data(parameter, location, hours)


@router.get("/trends/daily", summary="Analisis tren per hari", 
            response_model=Dict[str, Any])
async def get_daily_trend_endpoint(
    parameter: str = Query("temperature", description="Parameter sensor: 'temperature' atau 'humidity'"),
    location: Optional[str] = Query("all", description="Lokasi spesifik atau 'all' untuk semua lokasi"),
    days: int = Query(7, description="Jumlah hari data yang diambil (default: 7)", ge=1, le=90),
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil analisis tren per hari untuk parameter dan lokasi tertentu.
    Mendukung data hingga 90 hari ke belakang.
    Memerlukan autentikasi API Key.
    """
    return await get_daily_trend_data(parameter, location, days)


@router.get("/trends/monthly", summary="Analisis tren bulanan", 
            response_model=Dict[str, Any])
async def get_monthly_trend_endpoint(
    parameter: str = Query("temperature", description="Parameter sensor: 'temperature' atau 'humidity'"),
    location: Optional[str] = Query("all", description="Lokasi spesifik atau 'all' untuk semua lokasi"),
    days: int = Query(30, description="Jumlah hari data yang diambil (default: 30)", ge=7, le=365),
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil analisis tren bulanan untuk parameter dan lokasi tertentu.
    Mendukung data hingga 365 hari ke belakang.
    Memerlukan autentikasi API Key.
    """
    return await get_monthly_trend_data(parameter, location, days)


@router.get("/trends/compare", summary="Perbandingan tren antar periode", 
            response_model=Dict[str, Any])
async def get_comparative_trend_endpoint(
    parameter: str = Query("temperature", description="Parameter sensor: 'temperature' atau 'humidity'"),
    location: Optional[str] = Query("all", description="Lokasi spesifik atau 'all' untuk semua lokasi"),
    current_period: str = Query("7d", description="Periode saat ini (e.g., '7d', '30d')"),
    comparison_period: str = Query("7d", description="Periode pembanding (e.g., '7d', '30d')"),
    api_key: str = Depends(get_api_key)
):
    """
    Membandingkan tren periode saat ini dengan periode sebelumnya.
    Berguna untuk mengidentifikasi perubahan pola temporal.
    Memerlukan autentikasi API Key.
    """
    return await get_comparative_trend_analysis(parameter, location, current_period, comparison_period)


@router.get("/trends/summary", summary="Ringkasan analisis tren multi-parameter", 
            response_model=Dict[str, Any])
async def get_trend_summary_endpoint(
    location: Optional[str] = Query("all", description="Lokasi spesifik atau 'all' untuk semua lokasi"),
    period: str = Query("week", description="Periode analisis: 'day', 'week', atau 'month'"),
    api_key: str = Depends(get_api_key)
):
    """
    Memberikan ringkasan analisis tren untuk semua parameter (suhu dan kelembapan).
    Berguna untuk dashboard overview.
    Memerlukan autentikasi API Key.
    """
    try:
        # Ambil data untuk kedua parameter
        temperature_data = None
        humidity_data = None
        
        if period == "day":
            temperature_data = await get_hourly_trend_data("temperature", location, hours=24)
            humidity_data = await get_hourly_trend_data("humidity", location, hours=24)
        elif period == "week":
            temperature_data = await get_daily_trend_data("temperature", location, days=7)
            humidity_data = await get_daily_trend_data("humidity", location, days=7)
        elif period == "month":
            temperature_data = await get_monthly_trend_data("temperature", location, days=30)
            humidity_data = await get_monthly_trend_data("humidity", location, days=30)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Period '{period}' tidak didukung. Gunakan 'day', 'week', atau 'month'"
            )
        
        # Compile summary
        summary = {
            "location": location or "all",
            "period": period,
            "temperature": {
                "trend": temperature_data.get("analysis", {}).get("trend_direction", "unknown"),
                "current_avg": temperature_data.get("analysis", {}).get("statistics", {}).get("mean", 0),
                "volatility": temperature_data.get("analysis", {}).get("volatility", 0),
                "data_points": temperature_data.get("data_points", 0)
            },
            "humidity": {
                "trend": humidity_data.get("analysis", {}).get("trend_direction", "unknown"),
                "current_avg": humidity_data.get("analysis", {}).get("statistics", {}).get("mean", 0),
                "volatility": humidity_data.get("analysis", {}).get("volatility", 0),
                "data_points": humidity_data.get("data_points", 0)
            },
            "overall_assessment": _assess_overall_trend(temperature_data, humidity_data),
            "last_updated": datetime.now().isoformat()
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dalam ringkasan tren: {str(e)}")


def _assess_overall_trend(temperature_data: Dict[str, Any], humidity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Menilai tren keseluruhan berdasarkan data suhu dan kelembapan
    """
    temp_trend = temperature_data.get("analysis", {}).get("trend_direction", "unknown")
    humidity_trend = humidity_data.get("analysis", {}).get("trend_direction", "unknown")
    
    temp_volatility = temperature_data.get("analysis", {}).get("volatility", 0)
    humidity_volatility = humidity_data.get("analysis", {}).get("volatility", 0)
    
    # Assess stability
    if temp_volatility > 2 or humidity_volatility > 5:
        stability = "unstable"
    elif temp_volatility > 1 or humidity_volatility > 3:
        stability = "moderate"
    else:
        stability = "stable"
    
    # Assess direction consistency
    if temp_trend == humidity_trend:
        consistency = "consistent"
    elif temp_trend == "stable" or humidity_trend == "stable":
        consistency = "partially_consistent"
    else:
        consistency = "divergent"
    
    # Overall rating
    if stability == "stable" and consistency == "consistent":
        rating = "excellent"
    elif stability == "stable" and consistency == "partially_consistent":
        rating = "good"
    elif stability == "moderate":
        rating = "fair"
    else:
        rating = "concerning"
    
    return {
        "stability": stability,
        "consistency": consistency,
        "rating": rating,
        "temperature_trend": temp_trend,
        "humidity_trend": humidity_trend,
        "recommendations": _generate_trend_recommendations(temp_trend, humidity_trend, stability)
    }


def _generate_trend_recommendations(temp_trend: str, humidity_trend: str, stability: str) -> List[str]:
    """
    Generate rekomendasi berdasarkan analisis tren
    """
    recommendations = []
    
    if stability == "unstable":
        recommendations.append("Periksa sistem HVAC untuk fluktuasi yang tidak normal")
    
    if temp_trend == "increasing" and humidity_trend == "increasing":
        recommendations.append("Pertimbangkan peningkatan kapasitas pendinginan dan dehumidifikasi")
    elif temp_trend == "decreasing" and humidity_trend == "increasing":
        recommendations.append("Fokus pada sistem dehumidifikasi, suhu dalam rentang yang baik")
    elif temp_trend == "increasing" and humidity_trend == "decreasing":
        recommendations.append("Monitor keseimbangan iklim, mungkin perlu penyesuaian humidifikasi")
    
    if not recommendations:
        recommendations.append("Kondisi iklim dalam tren yang stabil")
    
    return recommendations
