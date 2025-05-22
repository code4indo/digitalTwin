"""
InfluxDB Service
Modul ini berisi fungsi-fungsi untuk berinteraksi dengan InfluxDB
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from influxdb_client.client.exceptions import InfluxDBError
from fastapi import HTTPException

# Import fungsi get_query_api dari stats_service
from services.stats_service import get_query_api

logger = logging.getLogger(__name__)


async def execute_query(query: str, description: str = "InfluxDB query") -> List[Any]:
    """
    Eksekusi query Flux di InfluxDB
    
    Args:
        query (str): Query Flux yang akan dieksekusi
        description (str, optional): Deskripsi query untuk logging. Default ke "InfluxDB query".
        
    Returns:
        List[Any]: Hasil query dari InfluxDB
        
    Raises:
        HTTPException: Jika terjadi error saat mengakses InfluxDB
    """
    q_api = get_query_api()
    
    try:
        logger.info(f"Menjalankan {description}: {query}")
        results = q_api.query(query=query)
        
        if not results:
            logger.info(f"{description} tidak mengembalikan data")
            return []
            
        return results
        
    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat {description}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat {description} dari InfluxDB: {e}", exc_info=True)
        detail_msg = f"Gagal {description} dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal {description} dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)


async def get_time_series_data(
    query: str, 
    description: str = "mengambil data time series"
) -> List[Dict[str, Any]]:
    """
    Mengambil data time series dari InfluxDB
    
    Args:
        query (str): Query Flux untuk data time series
        description (str, optional): Deskripsi query untuk logging
        
    Returns:
        List[Dict[str, Any]]: Daftar data time series
    """
    results = await execute_query(query, description)
    
    data_points = []
    for table in results:
        for record in table.records:
            data_points.append({
                "time": record.get_time(),
                "value": record.get_value(),
                "field": record.get_field(),
                "location": record.values.get("location"),
                "device_id": record.values.get("device_id")
            })
    
    return data_points


async def get_aggregated_data(
    query: str, 
    description: str = "mengambil data agregasi"
) -> Dict[str, Any]:
    """
    Mengambil data agregasi dari InfluxDB
    
    Args:
        query (str): Query Flux untuk data agregasi
        description (str, optional): Deskripsi query untuk logging
        
    Returns:
        Dict[str, Any]: Data agregasi
    """
    results = await execute_query(query, description)
    
    if not results or len(results) == 0 or len(results[0].records) == 0:
        return {
            "timestamp": datetime.now().isoformat()
        }
    
    return results[0].records[0].values
