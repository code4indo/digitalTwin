"""
Service untuk analisis tren data sensor
Berisi fungsi-fungsi untuk menganalisis pola temporal data
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import os

from fastapi import HTTPException
from influxdb_client.client.exceptions import InfluxDBError
from .stats_service import get_influx_client, get_query_api

# Import query functions dari trend_analysis
from flux_queries.trend_analysis import (
    get_hourly_aggregated_query,
    get_daily_aggregated_query,
    get_statistical_summary_query,
    get_moving_average_query,
    get_anomaly_detection_query,
    get_trend_direction_query,
    get_comparative_period_query
)

logger = logging.getLogger(__name__)

# Konfigurasi
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET_PRIMARY", "sensor_data_primary")

async def get_hourly_trend_data(
    parameter: str = "temperature",
    location: Optional[str] = None,
    hours: int = 24
) -> Dict[str, Any]:
    """
    Mendapatkan data tren per jam untuk parameter tertentu
    
    Args:
        parameter: Parameter yang dianalisis ('temperature' atau 'humidity')
        location: Lokasi spesifik (opsional, None untuk semua lokasi)
        hours: Jumlah jam data yang diambil (default 24)
    
    Returns:
        Dict berisi data tren per jam dengan analisis statistik
    """
    q_api = get_query_api()
    
    # Build location filter
    location_filter = ""
    if location and location != "all":
        location_filter = f'|> filter(fn: (r) => r["location"] == "{location}")'
    
    # Query untuk data per jam menggunakan function dari trend_analysis
    flux_query = get_hourly_aggregated_query(INFLUXDB_BUCKET, parameter, location_filter, hours)
    
    try:
        logger.info(f"Fetching hourly trend for {parameter}")
        logger.info(f"Using query: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0:
            return _generate_empty_trend_response(hours, "hourly", parameter, location or "all")
        
        # Process data
        timestamps = []
        values = []
        
        for table in result:
            for record in table.records:
                timestamps.append(record.get_time())
                values.append(record.get_value())
        
        if not values:
            return _generate_empty_trend_response(hours, "hourly", parameter, location or "all")
        
        # Sort by timestamp
        data_pairs = list(zip(timestamps, values))
        data_pairs.sort(key=lambda x: x[0])
        timestamps, values = zip(*data_pairs)
        
        # Calculate trend analysis
        trend_analysis = _calculate_trend_analysis(values, "hourly")
        
        # Format timestamps for display
        formatted_timestamps = [ts.strftime("%H:%M") for ts in timestamps]
        
        return {
            "period": "hourly",
            "parameter": parameter,
            "location": location or "all",
            "timestamps": formatted_timestamps,
            "values": [round(v, 1) for v in values],
            "analysis": trend_analysis,
            "data_points": len(values),
            "last_updated": datetime.now().isoformat()
        }
        
    except InfluxDBError as e:
        logger.error(f"InfluxDB error in hourly trend: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e.message}")
    except Exception as e:
        logger.error(f"Error in hourly trend analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_daily_trend_data(
    parameter: str = "temperature",
    location: Optional[str] = None,
    days: int = 7
) -> Dict[str, Any]:
    """
    Mendapatkan data tren harian untuk parameter tertentu
    
    Args:
        parameter: Parameter yang dianalisis ('temperature' atau 'humidity')
        location: Lokasi spesifik (opsional, None untuk semua lokasi)
        days: Jumlah hari data yang diambil (default 7)
    
    Returns:
        Dict berisi data tren harian dengan analisis statistik
    """
    q_api = get_query_api()
    
    # Build location filter
    location_filter = ""
    if location and location != "all":
        location_filter = f'|> filter(fn: (r) => r["location"] == "{location}")'
    
    # Query untuk data per hari menggunakan function dari trend_analysis
    flux_query = get_daily_aggregated_query(INFLUXDB_BUCKET, parameter, location_filter, days)
    
    try:
        logger.info(f"Fetching daily trend for {parameter}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0:
            return _generate_empty_trend_response(days, "daily", parameter, location or "all")
        
        # Process data
        timestamps = []
        values = []
        
        for table in result:
            for record in table.records:
                timestamps.append(record.get_time())
                values.append(record.get_value())
        
        if not values:
            return _generate_empty_trend_response(days, "daily", parameter, location or "all")
        
        # Sort by timestamp
        data_pairs = list(zip(timestamps, values))
        data_pairs.sort(key=lambda x: x[0])
        timestamps, values = zip(*data_pairs)
        
        # Calculate trend analysis
        trend_analysis = _calculate_trend_analysis(values, "daily")
        
        # Format timestamps for display
        formatted_timestamps = [ts.strftime("%Y-%m-%d") for ts in timestamps]
        
        return {
            "period": "daily",
            "parameter": parameter,
            "location": location or "all",
            "timestamps": formatted_timestamps,
            "values": [round(v, 1) for v in values],
            "analysis": trend_analysis,
            "data_points": len(values),
            "last_updated": datetime.now().isoformat()
        }
        
    except InfluxDBError as e:
        logger.error(f"InfluxDB error in daily trend: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e.message}")
    except Exception as e:
        logger.error(f"Error in daily trend analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_monthly_trend_data(
    parameter: str = "temperature",
    location: Optional[str] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Mendapatkan data tren bulanan untuk parameter tertentu
    
    Args:
        parameter: Parameter yang dianalisis ('temperature' atau 'humidity')
        location: Lokasi spesifik (opsional, None untuk semua lokasi)  
        days: Jumlah hari data yang diambil (default 30)
    
    Returns:
        Dict berisi data tren bulanan dengan analisis statistik
    """
    q_api = get_query_api()
    
    # Build location filter
    location_filter = ""
    if location and location != "all":
        location_filter = f'|> filter(fn: (r) => r["location"] == "{location}")'
    
    # Query untuk data per hari (untuk analisis bulanan) menggunakan function dari trend_analysis
    flux_query = get_daily_aggregated_query(INFLUXDB_BUCKET, parameter, location_filter, days)
    
    try:
        logger.info(f"Fetching monthly trend for {parameter}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0:
            return _generate_empty_trend_response(days, "monthly", parameter, location or "all")
        
        # Process data
        timestamps = []
        values = []
        
        for table in result:
            for record in table.records:
                timestamps.append(record.get_time())
                values.append(record.get_value())
        
        if not values:
            return _generate_empty_trend_response(days, "monthly", parameter, location or "all")
        
        # Sort by timestamp
        data_pairs = list(zip(timestamps, values))
        data_pairs.sort(key=lambda x: x[0])
        timestamps, values = zip(*data_pairs)
        
        # Calculate trend analysis
        trend_analysis = _calculate_trend_analysis(values, "monthly")
        
        # Format timestamps for display
        formatted_timestamps = [ts.strftime("%m-%d") for ts in timestamps]
        
        return {
            "period": "monthly",
            "parameter": parameter,
            "location": location or "all",
            "timestamps": formatted_timestamps,
            "values": [round(v, 1) for v in values],
            "analysis": trend_analysis,
            "data_points": len(values),
            "last_updated": datetime.now().isoformat()
        }
        
    except InfluxDBError as e:
        logger.error(f"InfluxDB error in monthly trend: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e.message}")
    except Exception as e:
        logger.error(f"Error in monthly trend analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _calculate_trend_analysis(values: List[float], period: str) -> Dict[str, Any]:
    """
    Menghitung analisis statistik untuk data tren
    
    Args:
        values: List nilai untuk dianalisis
        period: Periode data ("hourly", "daily", "monthly")
    
    Returns:
        Dict berisi analisis statistik
    """
    if not values or len(values) < 2:
        return {
            "trend_direction": "insufficient_data",
            "slope": 0,
            "correlation": 0,
            "moving_averages": [],
            "volatility": 0,
            "anomalies": []
        }
    
    try:
        values_array = np.array(values)
        x = np.arange(len(values))
        
        # Simple linear trend analysis using numpy
        slope = float(np.polyfit(x, values_array, 1)[0])
        correlation = float(np.corrcoef(x, values_array)[0, 1]) if len(values) > 1 else 0
        
        # Determine trend direction
        if abs(slope) < 0.01:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"
        
        # Calculate moving averages
        window_size = min(3, len(values) - 1) if period == "hourly" else min(7, len(values) - 1)
        if window_size > 0:
            moving_avg = pd.Series(values).rolling(window=window_size).mean().dropna().tolist()
            moving_avg = [round(v, 1) for v in moving_avg]
        else:
            moving_avg = []
        
        # Calculate volatility (standard deviation)
        volatility = float(np.std(values_array))
        
        # Simple anomaly detection (values beyond 2 standard deviations)
        mean_val = np.mean(values_array)
        std_val = np.std(values_array)
        anomaly_threshold = 2 * std_val
        
        anomalies = []
        for i, val in enumerate(values):
            if abs(val - mean_val) > anomaly_threshold:
                anomalies.append({
                    "index": i,
                    "value": round(val, 1),
                    "deviation": round(abs(val - mean_val), 1)
                })
        
        return {
            "trend_direction": trend_direction,
            "slope": round(slope, 4),
            "correlation": round(correlation, 3),
            "moving_averages": moving_avg,
            "volatility": round(volatility, 2),
            "anomalies": anomalies,
            "statistics": {
                "mean": round(float(np.mean(values_array)), 1),
                "median": round(float(np.median(values_array)), 1),
                "std": round(float(np.std(values_array)), 2),
                "min": round(float(np.min(values_array)), 1),
                "max": round(float(np.max(values_array)), 1),
                "q25": round(float(np.percentile(values_array, 25)), 1),
                "q75": round(float(np.percentile(values_array, 75)), 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in trend analysis calculation: {e}")
        return {
            "trend_direction": "analysis_error",
            "slope": 0,
            "correlation": 0,
            "moving_averages": [],
            "volatility": 0,
            "anomalies": [],
            "error": str(e)
        }


def _generate_empty_trend_response(period_count: int, period_type: str, parameter: str = "unknown", location: str = "all") -> Dict[str, Any]:
    """
    Generate empty response ketika tidak ada data
    """
    return {
        "period": period_type,
        "parameter": parameter,
        "location": location,
        "timestamps": [],
        "values": [],
        "analysis": {
            "trend_direction": "no_data",
            "slope": 0,
            "correlation": 0,
            "moving_averages": [],
            "volatility": 0,
            "anomalies": [],
            "statistics": {}
        },
        "data_points": 0,
        "last_updated": datetime.now().isoformat(),
        "message": "No data available for the specified parameters"
    }


async def get_comparative_trend_analysis(
    parameter: str = "temperature",
    location: Optional[str] = None,
    current_period: str = "7d",
    comparison_period: str = "7d"
) -> Dict[str, Any]:
    """
    Membandingkan tren periode saat ini dengan periode sebelumnya
    
    Args:
        parameter: Parameter yang dianalisis
        location: Lokasi spesifik
        current_period: Periode saat ini (e.g., "7d", "30d")
        comparison_period: Periode pembanding (e.g., "7d", "30d")
    
    Returns:
        Dict berisi perbandingan tren
    """
    q_api = get_query_api()
    
    location_filter = ""
    if location and location != "all":
        location_filter = f'|> filter(fn: (r) => r["location"] == "{location}")'
    
    # Query untuk periode saat ini
    current_query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -{current_period})
        |> filter(fn: (r) => r["_measurement"] == "sensor_data")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
        |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
        |> yield(name: "current_period")
    '''
    
    # Query untuk periode pembanding (periode sebelumnya)
    if current_period == "7d":
        comparison_start = "-14d"
        comparison_stop = "-7d"
    elif current_period == "30d":
        comparison_start = "-60d"
        comparison_stop = "-30d"
    else:
        comparison_start = f"-{int(current_period[:-1]) * 2}d"
        comparison_stop = f"-{current_period}"
    
    comparison_query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: {comparison_start}, stop: {comparison_stop})
        |> filter(fn: (r) => r["_measurement"] == "sensor_data")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
        |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
        |> yield(name: "comparison_period")
    '''
    
    try:
        # Execute both queries
        current_result = q_api.query(query=current_query)
        comparison_result = q_api.query(query=comparison_query)
        
        # Process current period data
        current_values = []
        if current_result:
            for table in current_result:
                for record in table.records:
                    current_values.append(record.get_value())
        
        # Process comparison period data
        comparison_values = []
        if comparison_result:
            for table in comparison_result:
                for record in table.records:
                    comparison_values.append(record.get_value())
        
        # Calculate comparison metrics
        comparison_analysis = _calculate_period_comparison(current_values, comparison_values)
        
        return {
            "parameter": parameter,
            "location": location or "all",
            "current_period": {
                "period": current_period,
                "data_points": len(current_values),
                "analysis": _calculate_trend_analysis(current_values, "daily") if current_values else {}
            },
            "comparison_period": {
                "period": comparison_period,
                "data_points": len(comparison_values),
                "analysis": _calculate_trend_analysis(comparison_values, "daily") if comparison_values else {}
            },
            "comparison": comparison_analysis,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in comparative trend analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _calculate_period_comparison(current_values: List[float], comparison_values: List[float]) -> Dict[str, Any]:
    """
    Menghitung perbandingan antara dua periode
    """
    if not current_values or not comparison_values:
        return {
            "change_percentage": 0,
            "change_direction": "insufficient_data",
            "significance": "unknown"
        }
    
    current_mean = np.mean(current_values)
    comparison_mean = np.mean(comparison_values)
    
    # Calculate percentage change
    if comparison_mean != 0:
        change_percentage = ((current_mean - comparison_mean) / comparison_mean) * 100
    else:
        change_percentage = 0
    
    # Determine change direction
    if abs(change_percentage) < 1:
        change_direction = "stable"
    elif change_percentage > 0:
        change_direction = "increased"
    else:
        change_direction = "decreased"
    
    # Determine significance level
    if abs(change_percentage) > 10:
        significance = "high"
    elif abs(change_percentage) > 5:
        significance = "moderate"
    else:
        significance = "low"
    
    return {
        "change_percentage": round(change_percentage, 2),
        "change_direction": change_direction,
        "significance": significance,
        "current_average": round(current_mean, 1),
        "comparison_average": round(comparison_mean, 1),
        "absolute_change": round(current_mean - comparison_mean, 1)
    }
