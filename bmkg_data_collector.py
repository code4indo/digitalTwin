import requests
import schedule
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import os # Ditambahkan untuk membaca environment variables

# --- Konfigurasi InfluxDB ---
# Mengambil konfigurasi dari environment variables, 
# dengan fallback ke nilai default jika variabel tidak diset.
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v") 
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "iot_project_alpha")    
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "sensor_data_primary")

# --- Konfigurasi BMKG API ---
BMKG_API_URL = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
KODE_WILAYAH = "31.74.06.1001" # Kode wilayah target

def fetch_bmkg_data():
    """Mengambil data prakiraan cuaca dari API BMKG."""
    full_url = f"{BMKG_API_URL}?adm4={KODE_WILAYAH}"
    try:
        response = requests.get(full_url, timeout=30)
        response.raise_for_status()  # Akan raise exception untuk status HTTP 4xx/5xx
        print(f"Successfully fetched data from BMKG for {KODE_WILAYAH}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching BMKG data: {e}")
        return None

def process_and_write_data(raw_data):
    """Memproses data JSON dari BMKG dan menuliskannya ke InfluxDB."""
    if not raw_data:
        return

    try:
        # Navigasi ke array data cuaca yang sebenarnya
        # Berdasarkan struktur: raw_data -> "data" (array) -> elemen ke-0 -> "cuaca" (array of arrays)
        weather_data_points = []
        if "data" in raw_data and len(raw_data["data"]) > 0:
            cuaca_days = raw_data["data"][0].get("cuaca", [])
            for day_forecasts in cuaca_days:
                for forecast in day_forecasts:
                    weather_data_points.append(forecast)
        
        if not weather_data_points:
            print("No weather data points found in the BMKG response.")
            return

        points_to_write = []
        for entry in weather_data_points:
            try:
                # Pastikan timestamp ada dan dalam format yang benar
                # BMKG API memberikan 'utc_datetime' sebagai "YYYY-MM-DD HH:MM:SS"
                # InfluxDB client mengharapkan objek datetime atau timestamp nanosecond
                dt_object = datetime.strptime(entry["utc_datetime"], "%Y-%m-%d %H:%M:%S")

                # Prepare visibility_km value
                visibility_raw = entry.get("vs_text", "").replace("> ", "").replace(" km", "").strip()
                visibility_val = None
                if visibility_raw: # Process only if not empty
                    try:
                        visibility_val = float(visibility_raw)
                    except ValueError:
                        visibility_val = visibility_raw # Keep as string if conversion fails
                
                point_builder = Point("bmkg_weather_forecast") \
                    .tag("source", "bmkg") \
                    .tag("kode_wilayah", KODE_WILAYAH) \
                    .tag("local_datetime", entry.get("local_datetime")) \
                    .tag("weather_desc", entry.get("weather_desc")) \
                    .tag("weather_desc_en", entry.get("weather_desc_en")) \
                    .tag("wd", entry.get("wd")) \
                    .field("temperature", float(entry.get("t", 0))) \
                    .field("humidity", float(entry.get("hu", 0))) \
                    .field("temperature_prediction", float(entry.get("tp", 0))) \
                    .field("tcc", float(entry.get("tcc", 0))) \
                    .field("wind_speed", float(entry.get("ws", 0))) \
                    .field("wind_direction_degree", float(entry.get("wd_deg", 0))) \
                
                if visibility_val is not None: # Add field only if it has a value
                    point_builder = point_builder.field("visibility_km", visibility_val)
                
                point = point_builder.time(dt_object, WritePrecision.S) # Menggunakan detik sebagai presisi
                                    
                points_to_write.append(point)
            except KeyError as ke:
                print(f"Skipping entry due to missing key: {ke} in entry: {entry}")
            except ValueError as ve:
                print(f"Skipping entry due to value error: {ve} in entry: {entry}")


        if points_to_write:
            with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                write_api.write(bucket=INFLUXDB_BUCKET, record=points_to_write)
                print(f"Successfully wrote {len(points_to_write)} points to InfluxDB for {KODE_WILAYAH}.")
        else:
            print("No valid points to write to InfluxDB.")

    except Exception as e:
        print(f"Error processing or writing data to InfluxDB: {e}")

def job():
    print(f"Running job at {time.ctime()}")
    data = fetch_bmkg_data()
    if data:
        process_and_write_data(data)

if __name__ == "__main__":
    print("BMKG Data Collector script started.")
    
    # Jalankan job pertama kali saat skrip dimulai
    job() 
    
    # Jadwalkan job untuk berjalan setiap 3 jam
    schedule.every(3).hours.do(job)
    # Anda juga bisa menggunakan interval lain, misal:
    # schedule.every(1).minutes.do(job) # Untuk testing

    while True:
        schedule.run_pending()
        time.sleep(1)