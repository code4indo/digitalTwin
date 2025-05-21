# api.py
import asyncio # Ditambahkan
import subprocess # Ditambahkan
import pandas as pd # Ditambahkan
import os
import logging
from datetime import datetime, timedelta # datetime dari datetime ditambahkan

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware  # Tambahkan import CORS middleware
from fastapi.security import APIKeyHeader
from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError # Pastikan ini diimpor jika endpoint lain membutuhkannya
from dotenv import load_dotenv
from pydantic import BaseModel

# Muat variabel lingkungan dari file .env
load_dotenv()

# Konfigurasi Logging Dasar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konfigurasi InfluxDB - Gunakan variabel lingkungan
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "iot_project_alpha")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET_PRIMARY", "sensor_data_primary")

# Konstanta untuk health check - tidak lagi digunakan oleh endpoint /system/health/ untuk jumlah perangkat
# ACTIVE_DEVICE_TIMESPAN_MINUTES = 10 
# TOTAL_DEVICE_TIMESPAN_DAYS = 90

# Path ke daftar perangkat dan variabel cache
DEVICE_LIST_PATH = "device_list.csv"
_device_ips_cache: Optional[List[str]] = None # Cache untuk daftar IP dari CSV

# Variabel global untuk caching hasil ping
_latest_ping_results: Dict[str, bool] = {}
_latest_ping_timestamp: Optional[datetime] = None
PING_RESULT_CACHE_SECONDS = 10 * 60  # 10 menit

# Konfigurasi Autentikasi API Key
API_KEY_NAME = "X-API-Key"
api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
VALID_API_KEYS_STR = os.getenv("VALID_API_KEYS", "") # Contoh: "key1,key2,secretkey"
VALID_API_KEYS = set(VALID_API_KEYS_STR.split(',')) if VALID_API_KEYS_STR else set()

if not VALID_API_KEYS and not os.getenv("SKIP_API_KEY_CHECK_FOR_DEV"): # Tambahkan SKIP_API_KEY_CHECK_FOR_DEV untuk memudahkan pengembangan lokal jika diperlukan
    logger.warning("VALID_API_KEYS tidak diset di environment. Autentikasi API Key mungkin tidak berfungsi sebagaimana mestinya.")

async def get_api_key(api_key: str = Depends(api_key_header_auth)):
    if not VALID_API_KEYS: # Jika tidak ada kunci yang dikonfigurasi, tolak semua untuk keamanan default
        logger.warning("Tidak ada VALID_API_KEYS yang dikonfigurasi. Menolak permintaan.")
        raise HTTPException(status_code=401, detail="Layanan tidak dikonfigurasi dengan benar untuk autentikasi.")
    if api_key not in VALID_API_KEYS:
        logger.warning(f"API Key tidak valid: {api_key}")
        raise HTTPException(status_code=401, detail="API Key tidak valid atau hilang")
    return api_key

app = FastAPI(
    title="Digital Twin Sensor API",
    description="API untuk mengakses data sensor yang dikumpulkan oleh Telegraf dan disimpan di InfluxDB. Memerlukan X-API-Key header untuk autentikasi.",
    version="1.2.0" # Versi diperbarui untuk mencerminkan penambahan endpoint health
)

# Konfigurasi CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3003") # Mendukung aplikasi React di port 3003
origins_list = origins.split(",") if origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

influx_client: Optional[InfluxDBClient] = None
query_api = None

@app.on_event("startup")
async def startup_event():
    global influx_client, query_api
    try:
        influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        query_api = influx_client.query_api()
        # Pindahkan pengecekan ping ke endpoint health check atau tempat yang lebih sesuai jika diperlukan pengecekan berkala
        # if influx_client.ping():
        #     logger.info("Berhasil terhubung ke InfluxDB.")
        # else:
        #     logger.error("Gagal terhubung ke InfluxDB (ping tidak berhasil). Harap periksa konfigurasi dan status InfluxDB.")
        #     influx_client = None # Set ke None jika ping gagal
        #     query_api = None
        # Cukup inisialisasi, biarkan endpoint health check yang melakukan ping aktif
        logger.info("InfluxDB client initialized. Connection status will be checked by health endpoint or on first query.")

    except Exception as e:
        logger.error(f"Error saat inisialisasi koneksi InfluxDB: {e}", exc_info=True)
        influx_client = None
        query_api = None

@app.on_event("shutdown")
async def shutdown_event():
    if influx_client:
        influx_client.close()
        logger.info("Koneksi InfluxDB ditutup.")

def get_query_api():
    if not query_api:
        logger.error("Koneksi ke InfluxDB belum siap atau gagal.")
        raise HTTPException(status_code=503, detail="Koneksi ke InfluxDB belum siap atau gagal. Periksa log server API.")
    return query_api

ALLOWED_AGGREGATE_FUNCTIONS = {"mean", "median", "sum", "count", "min", "max", "stddev", "first", "last"}

# Pydantic model untuk response status kesehatan sistem
class SystemHealthStatus(BaseModel):
    status: str
    active_devices: int
    total_devices: int
    ratio_active_to_total: float
    influxdb_connection: str

# Pydantic model untuk informasi status perangkat
class DeviceStatus(BaseModel):
    ip_address: str
    is_active: bool
    last_checked: datetime

# Pydantic model untuk response daftar status perangkat
class DeviceStatusResponse(BaseModel):
    devices: List[DeviceStatus]
    last_refresh_time: datetime

# Fungsi helper baru
def get_device_ips_from_csv() -> List[str]:
    global _device_ips_cache
    # Untuk saat ini, kita akan membaca ulang CSV setiap kali untuk memastikan daftar terbaru.
    # Jika file besar atau sering diakses, caching _device_ips_cache bisa dipertimbangkan kembali
    # dengan mekanisme invalidasi yang lebih baik (misalnya, berdasarkan timestamp file).
    # Namun, untuk daftar perangkat yang tidak sering berubah, pembacaan ulang sederhana sudah cukup.
    
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
        import socket
        
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

@app.get("/system/health/", response_model=SystemHealthStatus, summary="Dapatkan status kesehatan sistem secara real-time")
async def get_system_health_status(api_key: str = Depends(get_api_key)):
    global _latest_ping_results, _latest_ping_timestamp

    influxdb_ok = False
    if influx_client:
        try:
            influxdb_ok = influx_client.ping()
            logger.info("InfluxDB ping successful for health check.")
        except Exception as ping_exc:
            logger.warning(f"InfluxDB ping failed during health check: {ping_exc}", exc_info=True)
            influxdb_ok = False
    influxdb_connection_status = "connected" if influxdb_ok else "disconnected"

    device_ips = get_device_ips_from_csv()
    total_devices_count = len(device_ips)
    active_devices_count = 0
    
    now = datetime.now()
    
    perform_ping_refresh = True
    if _latest_ping_timestamp and (now - _latest_ping_timestamp).total_seconds() < PING_RESULT_CACHE_SECONDS:
        # Periksa apakah semua IP saat ini ada di cache dan jumlahnya sama
        # Ini untuk menangani kasus jika device_list.csv diubah (IP ditambah/dikurangi)
        cached_ips_set = set(_latest_ping_results.keys())
        current_ips_set = set(device_ips)
        if cached_ips_set == current_ips_set:
             perform_ping_refresh = False
             logger.info("Menggunakan hasil ping dari cache.")
             active_devices_count = sum(1 for ip in device_ips if _latest_ping_results.get(ip, False))
        else:
            logger.info("Daftar perangkat di CSV berubah sejak cache terakhir, melakukan refresh ping.")
    elif _latest_ping_timestamp:
        logger.info("Cache hasil ping kedaluwarsa, melakukan refresh ping.")
    else: # _latest_ping_timestamp is None
        logger.info("Tidak ada cache hasil ping, melakukan refresh ping.")

    if perform_ping_refresh:
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
            active_devices_count = current_active_count
            logger.info(f"Refresh ping selesai: {active_devices_count}/{total_devices_count} perangkat aktif. Hasil di-cache.")
        else:
            _latest_ping_results = {}
            _latest_ping_timestamp = now
            active_devices_count = 0
            logger.info("Tidak ada perangkat untuk di-ping. Cache dikosongkan.")
    
    ratio = 0.0
    system_status = "Critical" 

    if total_devices_count == 0:
        system_status = "No Devices Configured"
        active_devices_count = 0 
        ratio = 0.0
    else:
        ratio = active_devices_count / total_devices_count
        if not influxdb_ok: # Jika InfluxDB mati, sistem tidak bisa Optimal atau Good
             if ratio > 0.9: system_status = "Warning" # Optimal tapi DB down -> Warning
             elif ratio >= 0.75: system_status = "Warning" # Good tapi DB down -> Warning
             elif ratio >= 0.5: system_status = "Warning"
             else: system_status = "Critical"
        else: # InfluxDB OK
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
            system_status = "Warning" # Turunkan status jika DB bermasalah
        # Jika sudah Warning atau Critical karena rasio perangkat, biarkan.

    return SystemHealthStatus(
        status=system_status,
        active_devices=active_devices_count,
        total_devices=total_devices_count,
        ratio_active_to_total=round(ratio, 4),
        influxdb_connection=influxdb_connection_status
    )

@app.get("/devices/", summary="Daftar semua perangkat unik", response_model=List[Dict[str, Any]])
async def list_devices(api_key: str = Depends(get_api_key)): # Ditambahkan api_key dependency
    """
    Mengambil daftar perangkat unik (device_id dan lokasi terakhir yang diketahui) dari bucket InfluxDB.
    Memerlukan autentikasi API Key.
    """
    q_api = get_query_api()
    
    flux_query_ids = f'''
        import "influxdata/influxdb/schema"
        schema.tagValues(bucket: "{INFLUXDB_BUCKET}", tag: "device_id", start: -90d)
    '''
    try:
        logger.debug(f"Menjalankan Flux query untuk device ID: {flux_query_ids}")
        tables_ids = q_api.query(query=flux_query_ids)
        unique_device_ids = [row.values["_value"] for table in tables_ids for row in table.records]
        
        devices_with_location = []
        # TODO: Optimasi: Query ini dapat menyebabkan N+1 problem. Pertimbangkan untuk menggabungkannya menjadi satu query Flux jika memungkinkan.
        for dev_id in unique_device_ids:
            flux_query_loc = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -90d)
                  |> filter(fn: (r) => r.device_id == "{dev_id}" and exists r.location)
                  |> keep(columns: ["location", "_time"])
                  |> sort(columns: ["_time"], desc: true)
                  |> limit(n: 1)
                  |> yield(name: "last_location")
            '''
            logger.debug(f"Menjalankan Flux query untuk lokasi device {dev_id}: {flux_query_loc}")
            tables_loc = q_api.query(query=flux_query_loc)
            location = "N/A" # Default jika tidak ada lokasi
            if tables_loc and tables_loc[0].records: # Periksa apakah ada record
                location = tables_loc[0].records[0].values["location"]
            devices_with_location.append({"device_id": dev_id, "location": location})
        
        return devices_with_location

    except InfluxDBError as e:
        logger.error(f"InfluxDBError saat query perangkat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query perangkat dari InfluxDB: {e.message}")
    except Exception as e:
        logger.error(f"Error saat query perangkat dari InfluxDB: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query perangkat dari InfluxDB: {str(e)}")


@app.get("/data/", summary="Ambil data sensor dengan opsi agregasi", response_model=List[Dict[str, Any]])
async def get_sensor_data(
    start_time: Optional[datetime] = Query(None, description="Waktu mulai (format ISO, cth: 2023-01-01T00:00:00Z). Default: 1 jam terakhir."),
    end_time: Optional[datetime] = Query(None, description="Waktu selesai (format ISO, cth: 2023-01-01T01:00:00Z). Default: sekarang."),
    device_ids: Optional[List[str]] = Query(None, description="Daftar ID perangkat untuk difilter"),
    locations: Optional[List[str]] = Query(None, description="Daftar lokasi untuk difilter"),
    fields: Optional[List[str]] = Query(None, description="Kolom data spesifik yang ingin diambil (cth: temperature, humidity). Default: semua kolom data utama (temperature, humidity)."),
    limit: int = Query(100, ge=1, le=1000, description="Jumlah maksimum record yang dikembalikan per seri data (antara 1 dan 1000)"),
    measurement_name: str = Query("sensor_reading", description="Nama measurement di InfluxDB"),
    aggregate_window: Optional[str] = Query(None, description="Jendela agregasi (cth: '1h', '10m', '1d'). Memerlukan aggregate_function."),
    aggregate_function: Optional[str] = Query(None, description=f"Fungsi agregasi (cth: {', '.join(ALLOWED_AGGREGATE_FUNCTIONS)}). Memerlukan aggregate_window."),
    api_key: str = Depends(get_api_key) # Ditambahkan api_key dependency
):
    """
    Mengambil data sensor (suhu, kelembaban, dll.) dari InfluxDB.
    Memungkinkan filter berdasarkan rentang waktu, ID perangkat, lokasi, dan kolom data tertentu.
    Mendukung agregasi data menggunakan `aggregate_window` dan `aggregate_function`.
    Memerlukan autentikasi API Key.
    """
    q_api = get_query_api()

    range_filter_str = f'start: {start_time.isoformat() if start_time else "-1h"}'
    if end_time:
        range_filter_str += f', stop: {end_time.isoformat()}'
    
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
        # Default fields jika tidak ditentukan, bisa disesuaikan
        filters.append('(r._field == "temperature" or r._field == "humidity")')

    filter_expression = " and ".join(filters)
    
    aggregation_str = ""
    if aggregate_window and aggregate_function:
        if aggregate_function.lower() not in ALLOWED_AGGREGATE_FUNCTIONS:
            raise HTTPException(status_code=400, detail=f"Fungsi agregasi tidak valid: {aggregate_function}. Pilihan yang valid: {', '.join(ALLOWED_AGGREGATE_FUNCTIONS)}")
        # Pastikan aggregate_window adalah durasi yang valid (InfluxDB akan error jika tidak, tapi validasi regex sederhana bisa ditambahkan di sini jika perlu)
        aggregation_str = f'|> aggregateWindow(every: {aggregate_window}, fn: {aggregate_function.lower()}, createEmpty: false)'
    elif aggregate_window or aggregate_function: # Jika hanya salah satu yang diberikan
        raise HTTPException(status_code=400, detail="aggregate_window dan aggregate_function harus digunakan bersamaan.")

    flux_query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range({range_filter_str})
          |> filter(fn: (r) => {filter_expression})
          {aggregation_str} 
          |> pivot(rowKey:["_time", "device_id", "location", "source_ip", "hex_id_from_data"], columnKey: ["_field"], valueColumn: "_value")
          |> limit(n: {limit}) 
    '''
    # Catatan: Jika agregasi digunakan, 'source_ip' dan 'hex_id_from_data' dalam rowKey pivot mungkin perlu dipertimbangkan ulang
    # tergantung apakah field tersebut merupakan bagian dari group key yang dipertahankan oleh aggregateWindow.
    # Jika mereka adalah field biasa dan bukan tag, mereka mungkin hilang setelah agregasi.

    try:
        logger.info(f"Menjalankan Flux query untuk data (aggr_win='{aggregate_window}', aggr_func='{aggregate_function}'): {flux_query}")
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
        logger.error(f"InfluxDBError saat query data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gagal query data dari InfluxDB: {e.message}")
    except HTTPException: # Re-raise HTTPException agar tidak tertangkap oleh Exception umum
        raise
    except Exception as e:
        logger.error(f"Error saat query data dari InfluxDB: {e}", exc_info=True)
        detail_msg = f"Gagal query data dari InfluxDB: Terjadi kesalahan internal server." # Pesan generik untuk error tak terduga
        # Hindari membocorkan detail error internal yang sensitif ke klien
        if isinstance(e, ValueError) or isinstance(e, TypeError): # Contoh error yang mungkin aman untuk ditampilkan pesannya
             detail_msg = f"Gagal query data dari InfluxDB: {str(e)}"
        raise HTTPException(status_code=500, detail=detail_msg)

@app.get("/devices/status/", response_model=DeviceStatusResponse, summary="Dapatkan status aktif perangkat")
async def get_devices_status(api_key: str = Depends(get_api_key)):
    """
    Mengambil status aktif/tidak aktif dari perangkat yang terdaftar.
    Status ditentukan berdasarkan hasil ping terakhir.
    Memerlukan autentikasi API Key.
    """
    global _latest_ping_results, _latest_ping_timestamp

    device_ips = get_device_ips_from_csv()
    total_devices_count = len(device_ips)
    active_devices_count = 0
    
    now = datetime.now()

    # Jika tidak ada perangkat, langsung kembalikan response dengan daftar kosong
    if total_devices_count == 0:
        return DeviceStatusResponse(devices=[], last_refresh_time=now)

    # Periksa apakah hasil ping perlu di-refresh
    perform_ping_refresh = True
    if _latest_ping_timestamp and (now - _latest_ping_timestamp).total_seconds() < PING_RESULT_CACHE_SECONDS:
        # Gunakan hasil ping dari cache
        perform_ping_refresh = False
        logger.info("Menggunakan hasil ping dari cache.")
    elif _latest_ping_timestamp:
        logger.info("Cache hasil ping kedaluwarsa, melakukan refresh ping.")
    else: # _latest_ping_timestamp is None
        logger.info("Tidak ada cache hasil ping, melakukan refresh ping.")

    if perform_ping_refresh:
        current_ping_statuses_map = {}
        current_active_count = 0
        if total_devices_count > 0:
            ping_timeout_seconds = 1
            logger.info(f"Melakukan ping ke {total_devices_count} perangkat untuk status...")
            ping_tasks = [ping_device(ip, timeout_seconds=ping_timeout_seconds) for ip in device_ips]
            results = await asyncio.gather(*ping_tasks, return_exceptions=True)
            
            for i, res in enumerate(results):
                ip = device_ips[i]
                if isinstance(res, Exception):
                    logger.error(f"Exception saat ping ke {ip} selama refresh status: {res}", exc_info=True)
                    current_ping_statuses_map[ip] = False
                elif res is True:
                    current_active_count += 1
                    current_ping_statuses_map[ip] = True
                else: # res is False
                    current_ping_statuses_map[ip] = False
            
            _latest_ping_results = current_ping_statuses_map
            _latest_ping_timestamp = now
            active_devices_count = current_active_count
            logger.info(f"Refresh ping selesai untuk status: {active_devices_count}/{total_devices_count} perangkat aktif. Hasil di-cache.")
        else:
            _latest_ping_results = {}
            _latest_ping_timestamp = now
            active_devices_count = 0
            logger.info("Tidak ada perangkat untuk di-ping. Cache dikosongkan.")
    
    # Buat daftar status perangkat untuk response
    devices_status_list = []
    for ip in device_ips:
        devices_status_list.append({
            "ip_address": ip,
            "is_active": _latest_ping_results.get(ip, False),
            "last_checked": _latest_ping_timestamp if _latest_ping_results.get(ip, False) else None
        })
    
    return DeviceStatusResponse(
        devices=devices_status_list,
        last_refresh_time=now
    )

@app.get("/system/device_status/", response_model=DeviceStatusResponse, summary="Daftar status perangkat (aktif/tidak aktif)")
async def get_device_status(api_key: str = Depends(get_api_key)):
    """
    Menampilkan daftar semua perangkat dengan status aktif atau tidak aktif berdasarkan pemeriksaan ping terakhir.
    Memerlukan autentikasi API Key.
    
    - Status aktif (true) jika perangkat merespons ping
    - Status tidak aktif (false) jika perangkat tidak merespons ping
    - Waktu terakhir diperiksa menunjukkan kapan ping terakhir dilakukan
    """
    global _latest_ping_results, _latest_ping_timestamp
    
    # Jika tidak ada hasil ping sebelumnya, atau cache sudah kedaluwarsa, lakukan ping refresh
    now = datetime.now()
    if _latest_ping_timestamp is None or (now - _latest_ping_timestamp).total_seconds() >= PING_RESULT_CACHE_SECONDS:
        # Dapatkan status kesehatan untuk memperbarui _latest_ping_results
        await get_system_health_status(api_key)
    
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

# Untuk menjalankan aplikasi ini (misalnya dengan uvicorn):
# uvicorn api:app --reload
# Jangan lupa set variabel lingkungan VALID_API_KEYS, contoh:
# export VALID_API_KEYS="your_secret_api_key_1,another_key"
# Kemudian akses endpoint dengan header X-API-Key: your_secret_api_key_1
