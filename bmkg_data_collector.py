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
BMKG_API_URL = os.getenv("BMKG_API_URL", "https://api.bmkg.go.id/publik/prakiraan-cuaca")
# Kode wilayah dari environment variable dengan fallback ke nilai default
KODE_WILAYAH = os.getenv("BMKG_KODE_WILAYAH", "31.74.04.1003") # Menggunakan kode wilayah default

def fetch_bmkg_data():
    """Mengambil data prakiraan cuaca dari API BMKG."""
    full_url = f"{BMKG_API_URL}?adm4={KODE_WILAYAH}"
    print(f"Fetching data from URL: {full_url}")
    try:
        response = requests.get(full_url, timeout=30)
        response.raise_for_status()  # Akan raise exception untuk status HTTP 4xx/5xx
        print(f"Successfully fetched data from BMKG for {KODE_WILAYAH}")
        data = response.json()
        print(f"Response structure: {list(data.keys() if data else {})}")
        if "data" in data and len(data["data"]) > 0:
            print(f"Data points found for wilayah {KODE_WILAYAH}")
        else:
            print(f"No data points found for wilayah {KODE_WILAYAH}. Response: {data}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching BMKG data: {e}")
        return None

def process_and_write_data(raw_data):
    """Memproses data JSON dari BMKG dan menuliskannya ke InfluxDB."""
    if not raw_data:
        print("No raw data to process")
        return

    try:
        # Simpan informasi lokasi
        location_info = raw_data.get("lokasi", {})
        print(f"Location info: {location_info}")
        
        # Navigasi ke array data cuaca yang sebenarnya
        # Berdasarkan struktur: raw_data -> "data" (array) -> elemen ke-0 -> "cuaca" (array of arrays)
        weather_data_points = []
        location_details = {}
        
        if "data" in raw_data and len(raw_data["data"]) > 0:
            print(f"Raw data contains {len(raw_data['data'])} entries")
            data_entry = raw_data["data"][0]
            print(f"First data entry keys: {list(data_entry.keys() if data_entry else {})}")
            
            # Simpan informasi lokasi dari data entry
            location_details = data_entry.get("lokasi", {})
            print(f"Location details: {location_details}")
            
            cuaca_days = data_entry.get("cuaca", [])
            print(f"Found {len(cuaca_days)} days of weather forecast")
            for day_index, day_forecasts in enumerate(cuaca_days):
                print(f"Day {day_index+1} has {len(day_forecasts)} forecast entries")
                for forecast in day_forecasts:
                    weather_data_points.append(forecast)
        
        if not weather_data_points:
            print("No weather data points found in the BMKG response.")
            if "data" in raw_data:
                print(f"Raw data structure: {raw_data}")
            return

        points_to_write = []
        for entry in weather_data_points:
            try:
                # Pastikan timestamp ada dan dalam format yang benar
                # BMKG API memberikan 'utc_datetime' sebagai "YYYY-MM-DD HH:MM:SS"
                # InfluxDB client mengharapkan objek datetime atau timestamp nanosecond
                dt_object = datetime.strptime(entry["utc_datetime"], "%Y-%m-%d %H:%M:%S")

                # Prepare visibility_km value - ensure consistent typing
                visibility_raw = entry.get("vs_text", "").replace("> ", "").replace(" km", "").strip()
                visibility_val = None
                if visibility_raw: # Process only if not empty
                    try:
                        visibility_val = float(visibility_raw)
                    except ValueError:
                        # If conversion fails, set a default numeric value
                        visibility_val = 10.0  # Default visibility in km
                
                # Buat point dengan semua informasi yang tersedia
                point_builder = Point("bmkg_weather_forecast") \
                    .tag("source", "bmkg") \
                    .tag("kode_wilayah", KODE_WILAYAH)
                
                # Tambahkan informasi lokasi sebagai tags dan fields
                # Tags untuk filtering dan grouping
                for loc_key in ["provinsi", "kotkab", "kecamatan", "desa", "timezone"]:
                    if loc_key in location_details and location_details[loc_key]:
                        point_builder = point_builder.tag(loc_key, location_details.get(loc_key))
                        # Juga simpan sebagai field agar mudah diakses dalam query
                        point_builder = point_builder.field(f"loc_{loc_key}", location_details.get(loc_key))
                
                # Tambahkan time-related tags 
                for time_key in ["local_datetime", "time_index", "analysis_date"]:
                    if time_key in entry and entry[time_key]:
                        point_builder = point_builder.tag(time_key, entry.get(time_key))
                
                # Tambahkan weather description sebagai tag dan field
                for desc_key in ["weather_desc", "weather_desc_en", "wd", "wd_to"]:
                    if desc_key in entry and entry[desc_key]:
                        point_builder = point_builder.tag(desc_key, entry.get(desc_key))
                        # Juga simpan sebagai field untuk kemudahan query
                        point_builder = point_builder.field(f"desc_{desc_key}", entry.get(desc_key))
                
                # Tambahkan semua field numerik
                point_builder = point_builder \
                    .field("temperature", float(entry.get("t", 0))) \
                    .field("humidity", float(entry.get("hu", 0))) \
                    .field("temperature_prediction", float(entry.get("tp", 0))) \
                    .field("tcc", float(entry.get("tcc", 0))) \
                    .field("wind_speed", float(entry.get("ws", 0))) \
                    .field("wind_direction_degree", float(entry.get("wd_deg", 0))) \
                    .field("weather_code", int(entry.get("weather", 0))) \
                    .field("longitude", float(location_details.get("lon", 0))) \
                    .field("latitude", float(location_details.get("lat", 0)))
                
                # Tambahkan field visibility jika tersedia
                if visibility_val is not None:
                    point_builder = point_builder.field("visibility_km", visibility_val)
                
                # Tambahkan field visibility original
                if entry.get("vs") is not None:
                    point_builder = point_builder.field("visibility_raw", int(entry.get("vs", 0)))
                
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