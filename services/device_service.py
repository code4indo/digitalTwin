"""
Service layer untuk manajemen dan status perangkat
Berisi fungsi-fungsi untuk memantau status perangkat dan melakukan operasi terkait perangkat
"""

import logging
import pandas as pd
import os
import asyncio
import socket
from datetime import datetime
from typing import Dict, List, Optional, Any, Set

from fastapi import HTTPException
from pydantic import BaseModel

# Konstanta
DEVICE_LIST_PATH = "device_list.csv"
PING_RESULT_CACHE_SECONDS = 10 * 60  # 10 menit

# Variabel global untuk caching
_device_ips_cache: Optional[List[str]] = None
_latest_ping_results: Dict[str, bool] = {}
_latest_ping_timestamp: Optional[datetime] = None

logger = logging.getLogger(__name__)

# Model untuk status perangkat
class DeviceStatus(BaseModel):
    """Informasi status untuk satu perangkat"""
    ip_address: str  # Alamat IP perangkat
    is_active: bool  # Status aktif (true) atau tidak aktif (false)
    last_checked: datetime  # Waktu terakhir status diperiksa

# Model untuk respons status perangkat
class DeviceStatusResponse(BaseModel):
    """Hasil dari endpoint device status"""
    devices: List[DeviceStatus]  # Daftar status semua perangkat
    last_refresh_time: datetime  # Waktu terakhir status di-refresh

def get_device_ips_from_csv() -> List[str]:
    """
    Mendapatkan daftar IP perangkat dari file CSV
    
    Returns:
        List[str]: Daftar IP perangkat unik
    """
    global _device_ips_cache
    
    current_ips = []
    try:
        if not os.path.exists(DEVICE_LIST_PATH):
            logger.error(f"File daftar perangkat tidak ditemukan: {DEVICE_LIST_PATH}")
            return []
        df = pd.read_csv(DEVICE_LIST_PATH)
        if "IP ADDRESS" not in df.columns:
            logger.error(f"Kolom 'IP ADDRESS' tidak ditemukan di {DEVICE_LIST_PATH}")
            return []
        # Ambil IP unik dan hilangkan nilai NaN
        current_ips = df["IP ADDRESS"].dropna().astype(str).unique().tolist()
        logger.info(f"Berhasil memuat {len(current_ips)} IP perangkat unik dari {DEVICE_LIST_PATH}")
    except Exception as e:
        logger.error(f"Gagal membaca daftar perangkat dari {DEVICE_LIST_PATH}: {e}", exc_info=True)
        return [] # Kembalikan list kosong jika ada error

    # Update cache jika daftar IP berubah
    # Ini adalah invalidasi cache sederhana jika daftar IP aktual dari CSV berubah.
    if _device_ips_cache is None or set(_device_ips_cache) != set(current_ips):
        logger.info("Daftar IP perangkat berubah, cache hasil ping akan di-refresh pada pemeriksaan berikutnya.")
        global _latest_ping_timestamp # Tandai cache ping sebagai kedaluwarsa
        _latest_ping_timestamp = None 
    _device_ips_cache = current_ips
    return _device_ips_cache

async def ping_device(ip_address: str, timeout_seconds: int = 1) -> bool:
    """
    Melakukan ping ke perangkat untuk memeriksa apakah perangkat aktif
    
    Args:
        ip_address: Alamat IP perangkat
        timeout_seconds: Batas waktu tunggu ping dalam detik
        
    Returns:
        bool: True jika perangkat merespons, False jika tidak
    """
    # Pertama coba menggunakan ping
    try:
        command = ["ping", "-c", "1", f"-W", str(timeout_seconds), ip_address]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.debug(f"Ping ke {ip_address} berhasil.")
            return True
        else:
            # Tidak perlu log sebagai warning jika hanya gagal ping (perangkat offline)
            logger.debug(f"Ping ke {ip_address} gagal. Kode kembali: {process.returncode}. Stderr: {stderr.decode(errors='ignore').strip()}")
            return False
    except FileNotFoundError:
        logger.warning("Perintah 'ping' tidak ditemukan. Mencoba alternatif dengan socket...")
        # Metode alternatif menggunakan socket TCP
        
        # Port yang umum tersedia untuk dicek (port 7 adalah echo port)
        # Dalam kasus nyata, sesuaikan dengan port layanan yang diketahui berjalan di perangkat
        port_to_check = 7
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_seconds)
        
        try:
            # Coba membuat koneksi TCP
            result = sock.connect_ex((ip_address, port_to_check))
            sock.close()
            
            # Kode 0 berarti berhasil terhubung
            if result == 0:
                logger.debug(f"Koneksi socket ke {ip_address}:{port_to_check} berhasil.")
                return True
            else:
                logger.debug(f"Koneksi socket ke {ip_address}:{port_to_check} gagal.")
                return False
        except socket.error as e:
            logger.debug(f"Error socket saat mencoba terhubung ke {ip_address}:{port_to_check}: {e}")
            return False
    except Exception as e:
        logger.error(f"Error saat melakukan ping ke {ip_address}: {e}", exc_info=True)
        return False

async def refresh_device_status() -> Dict[str, bool]:
    """
    Melakukan refresh status semua perangkat dengan ping
    
    Returns:
        Dict[str, bool]: Map dari alamat IP ke status aktif (true/false)
    """
    global _latest_ping_results, _latest_ping_timestamp
    
    device_ips = get_device_ips_from_csv()
    total_devices_count = len(device_ips)
    now = datetime.now()
    
    current_ping_statuses_map = {}
    current_active_count = 0
    
    if total_devices_count > 0:
        ping_timeout_seconds = 1
        logger.info(f"Melakukan ping ke {total_devices_count} perangkat...")
        ping_tasks = [ping_device(ip, timeout_seconds=ping_timeout_seconds) for ip in device_ips]
        results = await asyncio.gather(*ping_tasks, return_exceptions=True)
        
        for i, res in enumerate(results):
            ip = device_ips[i]
            if isinstance(res, Exception):
                logger.error(f"Exception saat ping ke {ip} selama refresh: {res}", exc_info=True)
                current_ping_statuses_map[ip] = False
            elif res is True:
                current_active_count += 1
                current_ping_statuses_map[ip] = True
            else: # res is False
                current_ping_statuses_map[ip] = False
        
        _latest_ping_results = current_ping_statuses_map
        _latest_ping_timestamp = now
        logger.info(f"Refresh ping selesai: {current_active_count}/{total_devices_count} perangkat aktif. Hasil di-cache.")
    else:
        _latest_ping_results = {}
        _latest_ping_timestamp = now
        logger.info("Tidak ada perangkat untuk di-ping. Cache dikosongkan.")
    
    return _latest_ping_results

async def get_device_status() -> DeviceStatusResponse:
    """
    Mendapatkan status semua perangkat
    
    Returns:
        DeviceStatusResponse: Status semua perangkat
    """
    global _latest_ping_results, _latest_ping_timestamp
    
    # Jika tidak ada hasil ping sebelumnya, atau cache sudah kedaluwarsa, lakukan ping refresh
    now = datetime.now()
    if _latest_ping_timestamp is None or (now - _latest_ping_timestamp).total_seconds() >= PING_RESULT_CACHE_SECONDS:
        # Refresh status perangkat
        await refresh_device_status()
    
    # Dapatkan daftar perangkat dari CSV
    device_ips = get_device_ips_from_csv()
    
    # Buat daftar status perangkat
    device_statuses = []
    for ip in device_ips:
        is_active = _latest_ping_results.get(ip, False)
        device_statuses.append(DeviceStatus(
            ip_address=ip,
            is_active=is_active,
            last_checked=_latest_ping_timestamp or now
        ))
    
    return DeviceStatusResponse(
        devices=device_statuses,
        last_refresh_time=_latest_ping_timestamp or now
    )
