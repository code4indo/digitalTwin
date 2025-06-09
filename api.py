# api.py
import os
import logging
import asyncio
import socket
import pandas as pd
from datetime import datetime, timedelta

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends

# Import services akan dilakukan di masing-masing endpoint untuk menghindari circular import
# Services yang digunakan:
# - services.stats_service: layanan untuk statistik sensor
# - services.data_service: layanan untuk data sensor mentah
# - services.device_service: layanan untuk manajemen perangkat
# - services.health_service: layanan untuk pemantauan kesehatan sistem
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

# Variabel global untuk caching telah dipindahkan ke services/device_service.py

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

# Tambahkan router modular agar endpoint /stats/humidity/last-hour/stats/ dan lain-lain tersedia
from routes.stats_routes import router as stats_router
app.include_router(stats_router)

# Tambahkan router untuk endpoint rooms
from routes.room_routes import router as room_router
app.include_router(room_router)

# Tambahkan router untuk analisis tren
from routes.trend_routes import router as trend_router
app.include_router(trend_router)

# Tambahkan router untuk alerts
from routes.alert_routes import router as alert_router
app.include_router(alert_router)

# Tambahkan router untuk recommendations
from routes.recommendations_routes import router as recommendations_router
app.include_router(recommendations_router)

# Tambahkan router untuk automation
from routes.automation_routes import router as automation_router
app.include_router(automation_router)

# Tambahkan router untuk analysis
from routes.analysis_routes import router as analysis_router
app.include_router(analysis_router)

# Tambahkan router untuk external data
from routes.external_routes import router as external_router
app.include_router(external_router)

# Konfigurasi CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3003,http://10.13.0.4:3003") # Mendukung aplikasi React di localhost dan IP server
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

# Pydantic model for system health status has been moved to services/health_service.py

# Pydantic models for device status have been moved to services/device_service.py

# Helper functions for device management have been moved to services/device_service.py

@app.get("/system/health/", response_model=Dict[str, Any], summary="Dapatkan status kesehatan sistem secara real-time")
async def get_system_health_status(api_key: str = Depends(get_api_key)):
    """
    Memeriksa dan melaporkan status kesehatan sistem secara real-time.
    Status dapat berupa Optimal, Good, Warning, Critical, atau No Devices Configured.
    Status ditentukan berdasarkan rasio perangkat aktif dan status koneksi InfluxDB.
    Memerlukan autentikasi API Key.
    """
    # Import health service
    from services.health_service import get_system_health_status as health_service_get_status
    
    try:
        # Panggil fungsi service layer
        result = await health_service_get_status(influx_client)
        
        # Convert pydantic model to dict for response
        return result.dict()
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil status kesehatan sistem: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal saat mengambil status kesehatan sistem.")

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
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil data sensor (suhu, kelembaban, dll.) dari InfluxDB.
    Memungkinkan filter berdasarkan rentang waktu, ID perangkat, lokasi, dan kolom data tertentu.
    Mendukung agregasi data menggunakan `aggregate_window` dan `aggregate_function`.
    Memerlukan autentikasi API Key.
    """
    # Import service
    from services.data_service import get_sensor_data as data_service_get_sensor_data
    
    try:
        # Panggil fungsi service layer
        return await data_service_get_sensor_data(
            start_time=start_time,
            end_time=end_time,
            device_ids=device_ids,
            locations=locations,
            fields=fields,
            limit=limit,
            measurement_name=measurement_name,
            aggregate_window=aggregate_window,
            aggregate_function=aggregate_function
        )
    
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil data sensor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server saat mengambil data sensor.")


@app.get("/system/device_status/", response_model=Dict[str, Any], summary="Daftar status perangkat (aktif/tidak aktif)")
@app.get("/system/devices_status/", response_model=Dict[str, Any], include_in_schema=False) # Alias for compatibility with frontend
async def get_device_status(api_key: str = Depends(get_api_key)):
    """
    Menampilkan daftar semua perangkat dengan status aktif atau tidak aktif berdasarkan pemeriksaan ping terakhir.
    Memerlukan autentikasi API Key.
    
    - Status aktif (true) jika perangkat merespons ping
    - Status tidak aktif (false) jika perangkat tidak merespons ping
    - Waktu terakhir diperiksa menunjukkan kapan ping terakhir dilakukan
    """
    # Import service
    from services.device_service import get_device_status as device_service_get_status
    
    try:
        # Panggil fungsi service layer
        result = await device_service_get_status()
        
        # Convert pydantic model to dict for response
        return {
            "devices": [device.dict() for device in result.devices],
            "last_refresh_time": result.last_refresh_time
        }
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil status perangkat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server saat mengambil status perangkat.")

@app.get("/stats/temperature/", summary="Dapatkan statistik suhu dari seluruh perangkat", response_model=Dict[str, Any])
async def get_temperature_stats(
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
    # Import service
    from services.stats_service import get_temperature_stats as stats_service_get_temp_stats
    
    try:
        # Panggil fungsi service layer
        return await stats_service_get_temp_stats(start_time, end_time, locations)
    
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil statistik suhu: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server saat mengambil statistik suhu.")

@app.get("/stats/humidity/", summary="Dapatkan statistik kelembapan dari seluruh perangkat", response_model=Dict[str, Any])
async def get_humidity_stats(
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
    # Import service
    from services.stats_service import get_humidity_stats as stats_service_get_humidity_stats
    
    try:
        # Panggil fungsi service layer
        return await stats_service_get_humidity_stats(start_time, end_time, locations)
    
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil statistik kelembapan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server saat mengambil statistik kelembapan.")

@app.get("/stats/temperature/last-hour/", summary="Dapatkan suhu rata-rata seluruh perangkat pada jam terakhir", response_model=Dict[str, Any])
async def get_average_temperature_last_hour(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil suhu rata-rata dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    # Menggunakan stats_service untuk mengakses data
    from services.stats_service import get_average_temperature_last_hour as stats_service_get_avg_temp
    
    try:
        # Panggil fungsi service layer
        return await stats_service_get_avg_temp()
    
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil suhu rata-rata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server saat mengambil data suhu rata-rata.")

@app.get("/stats/humidity/last-hour/", summary="Dapatkan kelembaban rata-rata seluruh perangkat pada jam terakhir", response_model=Dict[str, Any])
async def get_average_humidity_last_hour(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil kelembaban rata-rata dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    # Menggunakan stats_service untuk mengakses data
    from services.stats_service import get_average_humidity_last_hour as stats_service_get_avg_hum
    
    try:
        # Panggil fungsi service layer
        return await stats_service_get_avg_hum()
    
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil kelembaban rata-rata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal saat mengambil kelembaban rata-rata.")

@app.get("/stats/temperature/last-hour/min/", summary="Dapatkan suhu minimum seluruh perangkat pada jam terakhir", response_model=Dict[str, Any])
async def get_min_temperature_last_hour(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil suhu minimum dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    # Menggunakan stats_service untuk mengakses data
    from services.stats_service import get_min_temperature_last_hour as stats_service_get_min_temp
    
    try:
        # Panggil fungsi service layer
        return await stats_service_get_min_temp()
    
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil suhu minimum: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server saat mengambil data suhu minimum.")


@app.get("/stats/temperature/last-hour/max/", summary="Dapatkan suhu maksimum seluruh perangkat pada jam terakhir", response_model=Dict[str, Any])
async def get_max_temperature_last_hour(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil suhu maksimum dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    # Menggunakan stats_service untuk mengakses data
    from services.stats_service import get_max_temperature_last_hour as stats_service_get_max_temp
    
    try:
        # Panggil fungsi service layer
        return await stats_service_get_max_temp()
    
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil suhu maksimum: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server saat mengambil data suhu maksimum.")


@app.get("/stats/temperature/last-hour/stats/", summary="Dapatkan statistik suhu seluruh perangkat pada jam terakhir", response_model=Dict[str, Any])
async def get_temperature_stats_last_hour(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil statistik suhu (rata-rata, min, max) dari seluruh perangkat pada rentang 1 jam terakhir.
    Memerlukan autentikasi API Key.
    """
    # Menggunakan stats_service untuk mengakses data
    from services.stats_service import get_temperature_stats_last_hour as stats_service_get_temp_stats
    
    try:
        # Panggil fungsi service layer
        return await stats_service_get_temp_stats()
    
    except HTTPException:
        # HTTPException dari service layer, teruskan ke client
        raise
    except Exception as e:
        # Error tak terduga
        logger.error(f"Error tak terduga saat mengambil statistik suhu: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server saat mengambil statistik suhu.")

# Untuk menjalankan aplikasi ini (misalnya dengan uvicorn):
# uvicorn api:app --host 0.0.0.0 --port 8002 --reload
# Jangan lupa set variabel lingkungan VALID_API_KEYS, contoh:
# export VALID_API_KEYS="your_secret_api_key_1,another_key"
# Kemudian akses endpoint dengan header X-API-Key: your_secret_api_key_1

# Jika file dijalankan langsung, mulai server uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
