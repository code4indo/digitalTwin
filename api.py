# api.py
import os
import logging # Ditambahkan
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends # Depends ditambahkan
from fastapi.security import APIKeyHeader # Ditambahkan
from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

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
    version="1.1.0" # Versi diperbarui
)

influx_client: Optional[InfluxDBClient] = None
query_api = None

@app.on_event("startup")
async def startup_event():
    global influx_client, query_api
    try:
        influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        query_api = influx_client.query_api()
        if influx_client.ping():
            logger.info("Berhasil terhubung ke InfluxDB.")
        else:
            logger.error("Gagal terhubung ke InfluxDB (ping tidak berhasil). Harap periksa konfigurasi dan status InfluxDB.")
            influx_client = None # Set ke None jika ping gagal
            query_api = None
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

# Untuk menjalankan aplikasi ini (misalnya dengan uvicorn):
# uvicorn api:app --reload
# Jangan lupa set variabel lingkungan VALID_API_KEYS, contoh:
# export VALID_API_KEYS="your_secret_api_key_1,another_key"
# Kemudian akses endpoint dengan header X-API-Key: your_secret_api_key_1
