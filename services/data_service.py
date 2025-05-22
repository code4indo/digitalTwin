"""
Implementasi service layer untuk data sensor API Digital Twin
Berisi fungsi-fungsi untuk mengakses dan memproses data sensor dari InfluxDB
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import os

from fastapi import HTTPException
from influxdb_client.client.exceptions import InfluxDBError

# Import konfigurasi dari environment
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET_PRIMARY", "sensor_data_primary")
ALLOWED_AGGREGATE_FUNCTIONS = {"mean", "median", "sum", "count", "min", "max", "stddev", "first", "last"}

# Import query helper dan query API
from services.stats_service import get_query_api
from flux_queries.data import get_general_sensor_data_query

logger = logging.getLogger(__name__)

async def get_sensor_data(
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    device_ids: Optional[List[str]],
    locations: Optional[List[str]],
    fields: Optional[List[str]],
    limit: int,
    measurement_name: str,
    aggregate_window: Optional[str],
    aggregate_function: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Mengambil data sensor dari InfluxDB dengan berbagai opsi filter dan agregasi
    
    Args:
        start_time: Waktu mulai untuk query
        end_time: Waktu selesai untuk query
        device_ids: Daftar ID perangkat untuk difilter
        locations: Daftar lokasi untuk difilter
        fields: Kolom data spesifik yang ingin diambil
        limit: Jumlah maksimum record yang dikembalikan
        measurement_name: Nama measurement di InfluxDB
        aggregate_window: Jendela agregasi
        aggregate_function: Fungsi agregasi
        
    Returns:
        List[Dict[str, Any]]: Data sensor dalam bentuk list of dictionary
        
    Raises:
        HTTPException: Jika terjadi error saat query
    """
    q_api = get_query_api()

    # Bangun string filter rentang waktu
    range_filter_str = f'start: {start_time.isoformat() if start_time else "-1h"}'
    if end_time:
        range_filter_str += f', stop: {end_time.isoformat()}'
    
    # Bangun filter expressions
    filters = [f'r._measurement == "{measurement_name}"']
    
    if device_ids:
        device_filter_parts = [f'r.device_id == "{did}"' for did in device_ids]
        filters.append(f"({' or '.join(device_filter_parts)})")
    
    if locations:
        location_filter_parts = [f'r.location == "{loc}"' for loc in locations]
        filters.append(f"({' or '.join(location_filter_parts)})")

    if fields:
        field_filter_parts = [f'r._field == "{f}"' for f in fields]
        filters.append(f"({' or '.join(field_filter_parts)})")
    else:
        # Default fields jika tidak ditentukan
        filters.append('(r._field == "temperature" or r._field == "humidity")')

    filter_expression = " and ".join(filters)
    
    # Bangun string agregasi
    aggregation_str = ""
    if aggregate_window and aggregate_function:
        if aggregate_function.lower() not in ALLOWED_AGGREGATE_FUNCTIONS:
            raise HTTPException(status_code=400, detail=f"Fungsi agregasi tidak valid: {aggregate_function}. Pilihan yang valid: {', '.join(ALLOWED_AGGREGATE_FUNCTIONS)}")
        aggregation_str = f'|> aggregateWindow(every: {aggregate_window}, fn: {aggregate_function.lower()}, createEmpty: false)'
    elif aggregate_window or aggregate_function:
        raise HTTPException(status_code=400, detail="aggregate_window dan aggregate_function harus digunakan bersamaan.")

    # Dapatkan query dari modul flux_queries
    flux_query = get_general_sensor_data_query(INFLUXDB_BUCKET, range_filter_str, filter_expression, aggregation_str, limit)
    
    try:
        logger.info(f"Menjalankan Flux query untuk data sensor: {flux_query}")
        result_df = q_api.query_data_frame(query=flux_query)
        
        if result_df is None:
            return []
        if isinstance(result_df, list): 
            all_records = []
            for df_item in result_df:
                if not df_item.empty:
                    # Ganti NaN/NaT dengan None untuk serialisasi JSON yang benar
                    df_item = df_item.where(pd.notnull(df_item), None) 
                    all_records.extend(df_item.to_dict(orient='records'))
            return all_records
        elif not result_df.empty:
            result_df = result_df.where(pd.notnull(result_df), None)
            return result_df.to_dict(orient='records')
        else:
            return []

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query data sensor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saat query data sensor dari InfluxDB: {e}", exc_info=True)
        detail_msg = "Gagal query data sensor dari InfluxDB: Terjadi kesalahan internal server."
        if isinstance(e, ValueError) or isinstance(e, TypeError):
            detail_msg = f"Gagal query data sensor dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)
