"""
Service untuk pemantauan kesehatan sistem
Berisi fungsi-fungsi untuk memeriksa status kesehatan sistem dan komponennya
"""

import logging
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel
from influxdb_client import InfluxDBClient

from services.device_service import refresh_device_status, get_device_ips_from_csv

logger = logging.getLogger(__name__)

# Model untuk status kesehatan sistem
class SystemHealthStatus(BaseModel):
    """Status kesehatan keseluruhan sistem"""
    status: str  # Status kesehatan sistem (Optimal, Good, Warning, Critical, No Devices Configured)
    active_devices: int  # Jumlah perangkat aktif
    total_devices: int  # Jumlah total perangkat terdaftar
    ratio_active_to_total: float  # Rasio perangkat aktif terhadap total
    influxdb_connection: str  # Status koneksi InfluxDB (connected, disconnected)

async def get_system_health_status(influx_client: InfluxDBClient) -> SystemHealthStatus:
    """
    Mendapatkan status kesehatan sistem secara real-time
    
    Args:
        influx_client: InfluxDB client
        
    Returns:
        SystemHealthStatus: Status kesehatan sistem
    """
    # Periksa koneksi InfluxDB
    influxdb_ok = False
    if influx_client:
        try:
            influxdb_ok = influx_client.ping()
            logger.info("InfluxDB ping successful for health check.")
        except Exception as ping_exc:
            logger.warning(f"InfluxDB ping failed during health check: {ping_exc}", exc_info=True)
            influxdb_ok = False
    influxdb_connection_status = "connected" if influxdb_ok else "disconnected"

    # Refresh status perangkat
    device_statuses = await refresh_device_status()
    
    # Hitung perangkat aktif dan total
    total_devices_count = len(device_statuses)
    active_devices_count = sum(1 for is_active in device_statuses.values() if is_active)
    
    # Hitung rasio dan tentukan status sistem
    ratio = 0.0
    system_status = "Critical"
    
    if total_devices_count == 0:
        system_status = "No Devices Configured"
        active_devices_count = 0
        ratio = 0.0
    else:
        ratio = active_devices_count / total_devices_count
        if not influxdb_ok:  # Jika InfluxDB mati, sistem tidak bisa Optimal atau Good
            if ratio > 0.9: system_status = "Warning"  # Optimal tapi DB down -> Warning
            elif ratio >= 0.75: system_status = "Warning"  # Good tapi DB down -> Warning
            elif ratio >= 0.5: system_status = "Warning"
            else: system_status = "Critical"
        else:  # InfluxDB OK
            if ratio > 0.9:
                system_status = "Optimal"
            elif ratio >= 0.75:
                system_status = "Good" 
            elif ratio >= 0.5:
                system_status = "Warning"
            else: 
                system_status = "Critical"
    
    # Logika tambahan jika InfluxDB mati, status tidak boleh "Optimal" atau "Good"
    if not influxdb_ok:
        if system_status == "Optimal" or system_status == "Good":
            system_status = "Warning"  # Turunkan status jika DB bermasalah
        # Jika sudah Warning atau Critical karena rasio perangkat, biarkan.
    
    return SystemHealthStatus(
        status=system_status,
        active_devices=active_devices_count,
        total_devices=total_devices_count,
        ratio_active_to_total=round(ratio, 4),
        influxdb_connection=influxdb_connection_status
    )
