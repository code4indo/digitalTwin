"""
Implementasi service layer untuk API Digital Twin
Berisi fungsi-fungsi untuk mengakses dan memproses data dari InfluxDB
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

from fastapi import HTTPException
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client import InfluxDBClient

# Import konfigurasi dari environment
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "iot_project_alpha")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET_PRIMARY", "sensor_data_primary")

# Import queries yang sudah dimodularisasi
from flux_queries import (
    get_temperature_stats_query,
    get_humidity_stats_query,
    get_environmental_stats_query,
    get_average_temperature_last_hour_query,
    get_min_temperature_last_hour_query,
    get_max_temperature_last_hour_query,
    get_temperature_stats_last_hour_query,
    get_average_humidity_last_hour_query,
    get_min_humidity_last_hour_query,
    get_max_humidity_last_hour_query,
    get_general_sensor_data_query,
    get_unique_devices_query,
)

logger = logging.getLogger(__name__)

# InfluxDB client singleton
_influx_client = None
_query_api = None

def get_influx_client():
    """
    Mendapatkan instance InfluxDB client (singleton pattern)
    
    Returns:
        InfluxDBClient: Instance InfluxDB client
    """
    global _influx_client
    
    if _influx_client is None:
        try:
            _influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        except Exception as e:
            logger.error(f"Error saat inisialisasi koneksi InfluxDB: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail="Gagal terhubung ke InfluxDB")
    
    return _influx_client

def get_query_api():
    """
    Mendapatkan query API dari InfluxDB client
    
    Returns:
        InfluxDBClient.query_api: Query API dari InfluxDB client
    """
    global _query_api
    
    if _query_api is None:
        client = get_influx_client()
        _query_api = client.query_api()
    
    return _query_api


async def get_average_temperature_last_hour() -> Dict[str, Any]:
    """
    Mendapatkan suhu rata-rata dari seluruh perangkat dalam rentang 1 jam terakhir
    
    Returns:
        Dict[str, Any]: Data suhu rata-rata dengan timestamp
    
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_average_temperature_last_hour_query(INFLUXDB_BUCKET)
    
    try:
        logger.info(f"Menjalankan Flux query untuk suhu rata-rata 1 jam terakhir: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0 or len(result[0].records) == 0:
            return {
                "avg_temperature": None,
                "timestamp": datetime.now().isoformat()
            }
        
        # Ambil hasil agregasi
        record = result[0].records[0]
        avg_temp = round(record.get_value(), 1)
        
        return {
            "avg_temperature": avg_temp,
            "timestamp": datetime.now().isoformat()
        }

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query suhu rata-rata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query suhu rata-rata dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query suhu rata-rata dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query suhu rata-rata dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_temperature_stats(start_time: Optional[datetime], end_time: Optional[datetime], 
                              locations: Optional[List[str]]) -> Dict[str, Any]:
    """
    Mendapatkan statistik suhu dari seluruh perangkat yang dimonitor
    
    Args:
        start_time (Optional[datetime]): Waktu mulai
        end_time (Optional[datetime]): Waktu selesai
        locations (Optional[List[str]]): Daftar lokasi untuk filter
        
    Returns:
        Dict[str, Any]: Data statistik suhu
        
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()

    # Bangun string filter waktu
    range_filter_str = f'start: {start_time.isoformat() if start_time else "-24h"}'
    if end_time:
        range_filter_str += f', stop: {end_time.isoformat()}'
    
    # Bangun filter lokasi
    location_filter = ""
    if locations:
        location_filter_parts = [f'r.location == "{loc}"' for loc in locations]
        location_filter = f' and ({" or ".join(location_filter_parts)})'
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_temperature_stats_query(INFLUXDB_BUCKET, range_filter_str, location_filter)
    
    try:
        logger.info(f"Menjalankan Flux query untuk statistik suhu: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result:
            # Tidak ada data yang ditemukan
            return {
                "avg_temperature": None,
                "min_temperature": None,
                "max_temperature": None,
                "sample_count": 0
            }
        
        # Ambil hasil agregasi
        record = result[0].records[0]
        stats = {
            "avg_temperature": round(record.values.get("avg_temperature", 0), 1) if record.values.get("avg_temperature") is not None else None,
            "min_temperature": round(record.values.get("min_temperature", 0), 1) if record.values.get("min_temperature") is not None else None,
            "max_temperature": round(record.values.get("max_temperature", 0), 1) if record.values.get("max_temperature") is not None else None,
            "sample_count": int(record.values.get("sample_count", 0))
        }
        
        return stats

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query statistik suhu: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query statistik suhu dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query statistik suhu dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query statistik suhu dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_humidity_stats(start_time: Optional[datetime], end_time: Optional[datetime],
                           locations: Optional[List[str]]) -> Dict[str, Any]:
    """
    Mendapatkan statistik kelembaban dari seluruh perangkat yang dimonitor
    
    Args:
        start_time (Optional[datetime]): Waktu mulai
        end_time (Optional[datetime]): Waktu selesai
        locations (Optional[List[str]]): Daftar lokasi untuk filter
        
    Returns:
        Dict[str, Any]: Data statistik kelembaban
        
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()

    # Bangun string filter waktu
    range_filter_str = f'start: {start_time.isoformat() if start_time else "-24h"}'
    if end_time:
        range_filter_str += f', stop: {end_time.isoformat()}'
    
    # Bangun filter lokasi
    location_filter = ""
    if locations:
        location_filter_parts = [f'r.location == "{loc}"' for loc in locations]
        location_filter = f' and ({" or ".join(location_filter_parts)})'
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_humidity_stats_query(INFLUXDB_BUCKET, range_filter_str, location_filter)
    
    try:
        logger.info(f"Menjalankan Flux query untuk statistik kelembaban: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result:
            # Tidak ada data yang ditemukan
            return {
                "avg_humidity": None,
                "min_humidity": None,
                "max_humidity": None,
                "sample_count": 0
            }
        
        # Ambil hasil agregasi
        record = result[0].records[0]
        stats = {
            "avg_humidity": round(record.values.get("avg_humidity", 0), 0) if record.values.get("avg_humidity") is not None else None,
            "min_humidity": round(record.values.get("min_humidity", 0), 0) if record.values.get("min_humidity") is not None else None,
            "max_humidity": round(record.values.get("max_humidity", 0), 0) if record.values.get("max_humidity") is not None else None,
            "sample_count": int(record.values.get("sample_count", 0))
        }
        
        return stats

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query statistik kelembaban: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query statistik kelembaban dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query statistik kelembaban dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query statistik kelembaban dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_environmental_stats(start_time: Optional[datetime], end_time: Optional[datetime],
                                locations: Optional[List[str]]) -> Dict[str, Any]:
    """
    Mendapatkan statistik lingkungan (suhu dan kelembaban) dari seluruh perangkat yang dimonitor
    
    Args:
        start_time (Optional[datetime]): Waktu mulai
        end_time (Optional[datetime]): Waktu selesai
        locations (Optional[List[str]]): Daftar lokasi untuk filter
        
    Returns:
        Dict[str, Any]: Data statistik lingkungan
        
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()

    # Bangun string filter waktu
    range_filter_str = f'start: {start_time.isoformat() if start_time else "-24h"}'
    if end_time:
        range_filter_str += f', stop: {end_time.isoformat()}'
    
    # Bangun filter lokasi
    location_filter = ""
    if locations:
        location_filter_parts = [f'r.location == "{loc}"' for loc in locations]
        location_filter = f' and ({" or ".join(location_filter_parts)})'
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_environmental_stats_query(INFLUXDB_BUCKET, range_filter_str, location_filter)
    
    try:
        logger.info(f"Menjalankan Flux query untuk statistik lingkungan: {flux_query}")
        results = q_api.query(query=flux_query)
        
        stats = {
            "temperature": {
                "avg": None,
                "min": None,
                "max": None,
                "sample_count": 0
            },
            "humidity": {
                "avg": None,
                "min": None,
                "max": None,
                "sample_count": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Proses hasil query
        for table in results:
            for record in table.records:
                measurement = record.values.get("_measurement")
                if measurement == "temperature":
                    stats["temperature"]["avg"] = round(record.values.get("avg", 0), 1) if record.values.get("avg") is not None else None
                    stats["temperature"]["min"] = round(record.values.get("min", 0), 1) if record.values.get("min") is not None else None
                    stats["temperature"]["max"] = round(record.values.get("max", 0), 1) if record.values.get("max") is not None else None
                    stats["temperature"]["sample_count"] = int(record.values.get("sample_count", 0))
                elif measurement == "humidity":
                    stats["humidity"]["avg"] = round(record.values.get("avg", 0), 0) if record.values.get("avg") is not None else None
                    stats["humidity"]["min"] = round(record.values.get("min", 0), 0) if record.values.get("min") is not None else None
                    stats["humidity"]["max"] = round(record.values.get("max", 0), 0) if record.values.get("max") is not None else None
                    stats["humidity"]["sample_count"] = int(record.values.get("sample_count", 0))
        
        return stats

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query statistik lingkungan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query statistik lingkungan dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query statistik lingkungan dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query statistik lingkungan dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_average_humidity_last_hour() -> Dict[str, Any]:
    """
    Mendapatkan kelembaban rata-rata dari seluruh perangkat dalam rentang 1 jam terakhir
    
    Returns:
        Dict[str, Any]: Data kelembaban rata-rata dengan timestamp
    
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_average_humidity_last_hour_query(INFLUXDB_BUCKET)
    
    try:
        logger.info(f"Menjalankan Flux query untuk kelembaban rata-rata 1 jam terakhir: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0 or len(result[0].records) == 0:
            return {
                "avg_humidity": None,
                "timestamp": datetime.now().isoformat()
            }
        
        # Ambil hasil agregasi
        record = result[0].records[0]
        avg_humidity = round(record.get_value(), 0)
        
        return {
            "avg_humidity": avg_humidity,
            "timestamp": datetime.now().isoformat()
        }

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query kelembaban rata-rata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query kelembaban rata-rata dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query kelembaban rata-rata dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query kelembaban rata-rata dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_min_humidity_last_hour() -> Dict[str, Any]:
    """
    Mendapatkan kelembaban minimum dari seluruh perangkat dalam rentang 1 jam terakhir
    
    Returns:
        Dict[str, Any]: Data kelembaban minimum dengan timestamp
    
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_min_humidity_last_hour_query(INFLUXDB_BUCKET)
    
    try:
        logger.info(f"Menjalankan Flux query untuk kelembaban minimum 1 jam terakhir: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0 or len(result[0].records) == 0:
            return {
                "min_humidity": None,
                "timestamp": datetime.now().isoformat()
            }
        
        # Ambil hasil agregasi
        record = result[0].records[0]
        min_humidity = round(record.get_value(), 0)
        
        return {
            "min_humidity": min_humidity,
            "timestamp": datetime.now().isoformat()
        }

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query kelembaban minimum: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query kelembaban minimum dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query kelembaban minimum dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query kelembaban minimum dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_max_humidity_last_hour() -> Dict[str, Any]:
    """
    Mendapatkan kelembaban maksimum dari seluruh perangkat dalam rentang 1 jam terakhir
    
    Returns:
        Dict[str, Any]: Data kelembaban maksimum dengan timestamp
    
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_max_humidity_last_hour_query(INFLUXDB_BUCKET)
    
    try:
        logger.info(f"Menjalankan Flux query untuk kelembaban maksimum 1 jam terakhir: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0 or len(result[0].records) == 0:
            return {
                "max_humidity": None,
                "timestamp": datetime.now().isoformat()
            }
        
        # Ambil hasil agregasi
        record = result[0].records[0]
        max_humidity = round(record.get_value(), 0)
        
        return {
            "max_humidity": max_humidity,
            "timestamp": datetime.now().isoformat()
        }

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query kelembaban maksimum: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query kelembaban maksimum dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query kelembaban maksimum dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query kelembaban maksimum dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_humidity_stats_last_hour() -> Dict[str, Any]:
    """
    Mendapatkan statistik kelembaban (rata-rata, minimum, maksimum) dari seluruh perangkat dalam 1 jam terakhir
    
    Returns:
        Dict[str, Any]: Data statistik kelembaban dengan timestamp
    
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    try:
        # Mendapatkan semua data secara parallel
        avg_data = await get_average_humidity_last_hour()
        min_data = await get_min_humidity_last_hour()
        max_data = await get_max_humidity_last_hour()
        
        # Gabungkan hasil
        return {
            "avg_humidity": avg_data.get("avg_humidity"),
            "min_humidity": min_data.get("min_humidity"),
            "max_humidity": max_data.get("max_humidity"),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat mengambil statistik kelembaban 1 jam terakhir: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal mengambil statistik kelembaban: Terjadi kesalahan internal server.")


async def get_min_temperature_last_hour() -> Dict[str, Any]:
    """
    Mendapatkan suhu minimum dari seluruh perangkat dalam rentang 1 jam terakhir
    
    Returns:
        Dict[str, Any]: Data suhu minimum dengan timestamp
    
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_min_temperature_last_hour_query(INFLUXDB_BUCKET)
    
    try:
        logger.info(f"Menjalankan Flux query untuk suhu minimum 1 jam terakhir: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0 or len(result[0].records) == 0:
            return {
                "min_temperature": None,
                "timestamp": datetime.now().isoformat()
            }
        
        # Ambil hasil agregasi
        record = result[0].records[0]
        min_temp = round(record.get_value(), 1)
        
        return {
            "min_temperature": min_temp,
            "timestamp": datetime.now().isoformat()
        }

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query suhu minimum: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query suhu minimum dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query suhu minimum dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query suhu minimum dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_max_temperature_last_hour() -> Dict[str, Any]:
    """
    Mendapatkan suhu maksimum dari seluruh perangkat dalam rentang 1 jam terakhir
    
    Returns:
        Dict[str, Any]: Data suhu maksimum dengan timestamp
    
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_max_temperature_last_hour_query(INFLUXDB_BUCKET)
    
    try:
        logger.info(f"Menjalankan Flux query untuk suhu maksimum 1 jam terakhir: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0 or len(result[0].records) == 0:
            return {
                "max_temperature": None,
                "timestamp": datetime.now().isoformat()
            }
        
        # Ambil hasil agregasi
        record = result[0].records[0]
        max_temp = round(record.get_value(), 1)
        
        return {
            "max_temperature": max_temp,
            "timestamp": datetime.now().isoformat()
        }

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query suhu maksimum: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query suhu maksimum dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query suhu maksimum dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query suhu maksimum dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_temperature_stats_last_hour() -> Dict[str, Any]:
    """
    Mendapatkan statistik suhu (rata-rata, min, max) dari seluruh perangkat dalam rentang 1 jam terakhir
    
    Returns:
        Dict[str, Any]: Data statistik suhu dengan timestamp
    
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()
    
    # Dapatkan query dari modul flux_queries
    flux_query = get_temperature_stats_last_hour_query(INFLUXDB_BUCKET)
    
    try:
        logger.info(f"Menjalankan Flux query untuk statistik suhu 1 jam terakhir: {flux_query}")
        result = q_api.query(query=flux_query)
        
        if not result or len(result) == 0 or len(result[0].records) == 0:
            return {
                "avg_temperature": None,
                "min_temperature": None,
                "max_temperature": None,
                "timestamp": datetime.now().isoformat()
            }
        
        # Ambil hasil agregasi
        record = result[0].records[0]
        
        return {
            "avg_temperature": round(record.values.get("avg_temperature", 0), 1),
            "min_temperature": round(record.values.get("min_temperature", 0), 1),
            "max_temperature": round(record.values.get("max_temperature", 0), 1),
            "timestamp": datetime.now().isoformat()
        }

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query statistik suhu: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query statistik suhu dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query statistik suhu dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query statistik suhu dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)
