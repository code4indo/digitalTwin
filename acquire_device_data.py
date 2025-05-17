import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import os # Untuk membaca variabel environment jika diperlukan
import csv
import threading

# --- Konfigurasi InfluxDB ---
INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN", "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "iot_project_alpha")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET", "sensor_data_primary")

# --- Konfigurasi Umum ---
DEVICE_CSV_PATH = "/home/lambda_one/project/digitalTwin/device_list.csv" # Path ke file CSV perangkat
POLL_INTERVAL_SECONDS = 10 # Seberapa sering mengambil data dari SEMUA perangkat (dalam detik)
REQUEST_TIMEOUT_SECONDS = 5 # Timeout untuk permintaan HTTP ke perangkat

# --- Inisialisasi Klien InfluxDB ---
client = None # Akan diinisialisasi di blok try utama
write_api = None # Akan diinisialisasi di blok try utama

def load_devices(csv_path):
    """Membaca daftar perangkat dari file CSV."""
    devices = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            if not reader.fieldnames: # Tambahkan pengecekan ini
                print(f"Error: Tidak dapat membaca header dari file CSV '{csv_path}'. Pastikan file tidak kosong, memiliki header yang valid, dan menggunakan encoding UTF-8.")
                return []

            required_columns = ['IP ADDRESS', 'ID LOGGER', 'LOKASI']
            # Memastikan kolom yang dibutuhkan ada
            if not all(col in reader.fieldnames for col in required_columns):
                missing_cols = [col for col in required_columns if col not in reader.fieldnames]
                present_cols = list(reader.fieldnames) if reader.fieldnames else []
                print(f"Error: File CSV '{csv_path}' kekurangan kolom yang dibutuhkan: {', '.join(missing_cols)}. Kolom yang terdeteksi: {', '.join(present_cols)}.")
                return []
                
            for row_number, row in enumerate(reader, 1): # Mulai dari baris 1 untuk data (setelah header)
                # Validasi dasar bahwa kolom yang diharapkan ada di baris tersebut (meskipun DictReader seharusnya menanganinya)
                if not all(col in row for col in required_columns):
                    print(f"Warning: Baris {row_number + 1} di '{csv_path}' mungkin kekurangan beberapa kolom yang diharapkan. Baris dilewati: {row}")
                    continue

                ip_address = row.get('IP ADDRESS', '').strip() # Gunakan .get() untuk keamanan
                id_logger = row.get('ID LOGGER', '').strip()
                lokasi = row.get('LOKASI', '').strip()
                
                if ip_address and id_logger and lokasi: # Hanya proses jika semua field penting ada
                    devices.append({
                        "id_logger": id_logger,
                        "lokasi": lokasi,
                        "ip_address": ip_address,
                        "url": f"http://{ip_address}/"
                    })
                elif ip_address: # Jika hanya IP yang ada, mungkin masih berguna untuk log error, tapi tidak untuk diproses penuh
                    print(f"Warning: Baris {row_number + 1} di '{csv_path}' dengan IP '{ip_address}' kekurangan ID Logger atau Lokasi. Baris tidak diproses sepenuhnya.")
                # Jika IP address kosong, baris akan dilewati secara diam-diam oleh logika 'if ip_address' sebelumnya.

    except FileNotFoundError:
        print(f"Error: File CSV perangkat tidak ditemukan di '{csv_path}'")
        return []
    except Exception as e:
        print(f"Error saat membaca file CSV perangkat '{csv_path}': {e}")
        return []
    if not devices:
        print(f"Tidak ada perangkat yang dimuat dari '{csv_path}'. Pastikan file tidak kosong dan formatnya benar.")
    return devices

def fetch_and_parse_device_data(url, device_ip_for_log): # device_ip_for_log ditambahkan untuk logging yang lebih baik
    """
    Mengambil data dari URL perangkat dan mem-parsingnya.
    Contoh data: "46#22.20#2D303D" atau HTML seperti "<meta...><body>46#22.20#2D303D</body>"
    Mengembalikan dictionary: {"humidity": float, "temperature": float, "hex_value": str} atau None jika error.
    """
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        
        raw_data = response.text.strip()
        data_to_parse = raw_data

        body_start_tag = "<body>"
        body_end_tag = "</body>"
        
        idx_body_start = raw_data.find(body_start_tag)
        if idx_body_start != -1:
            idx_body_end = raw_data.find(body_end_tag, idx_body_start + len(body_start_tag))
            if idx_body_end != -1:
                data_to_parse = raw_data[idx_body_start + len(body_start_tag):idx_body_end].strip()
        
        parts = data_to_parse.split('#')
        
        if len(parts) == 3:
            humidity = float(parts[0])
            temperature = float(parts[1])
            hex_value = parts[2]
            return {"humidity": humidity, "temperature": temperature, "hex_value": hex_value}
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip_for_log}] Error: Format data tidak sesuai. Diterima (setelah potensi ekstraksi HTML): '{data_to_parse}'")
            return None
    except requests.exceptions.Timeout:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip_for_log}] Error: Timeout mengambil data dari {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip_for_log}] Error mengambil data dari {url}: {e}")
        return None
    except ValueError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip_for_log}] Error mem-parsing nilai numerik dari data '{data_to_parse if 'data_to_parse' in locals() else raw_data}': {e}")
        return None
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip_for_log}] Error tidak diketahui saat memproses data dari {url}: {e}")
        return None

def process_single_device(device_info, local_write_api, bucket, org):
    """Memproses satu perangkat: fetch, parse, dan write ke InfluxDB."""
    device_url = device_info["url"]
    device_ip = device_info["ip_address"] # Untuk logging
    id_logger = device_info["id_logger"]
    lokasi = device_info["lokasi"]

    # print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip}] Memulai pengambilan data...")
    parsed_data = fetch_and_parse_device_data(device_url, device_ip)
    
    if parsed_data:
        point = Point("device_readings") \
            .tag("device_ip", device_ip) \
            .tag("id_logger", id_logger) \
            .tag("lokasi", lokasi) \
            .tag("source_url", device_url) \
            .field("humidity", parsed_data["humidity"]) \
            .field("temperature", parsed_data["temperature"]) \
            .field("status_hex", parsed_data["hex_value"]) \
            .time(time.time_ns(), WritePrecision.NS)
        
        try:
            if local_write_api: # Pastikan write_api sudah diinisialisasi
                local_write_api.write(bucket=bucket, org=org, record=point)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip}] Data berhasil ditulis: {point.to_line_protocol()}")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip}] Error: write_api InfluxDB belum diinisialisasi.")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip}] Error menulis ke InfluxDB: {e}")
    # else: # Pesan error sudah dicetak oleh fetch_and_parse_device_data
        # print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Device: {device_ip}] Gagal mendapatkan atau mem-parsing data.")

if __name__ == "__main__":
    try:
        # Inisialisasi klien InfluxDB dipindahkan ke sini agar bisa diakses global setelah pengecekan
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        if not client.ping():
            raise Exception("Koneksi ke InfluxDB gagal. Pastikan URL, Token, dan Org benar, dan InfluxDB berjalan.")
        print(f"Berhasil terhubung ke InfluxDB di {INFLUX_URL}")

        devices = load_devices(DEVICE_CSV_PATH)
        if not devices:
            print("Tidak ada perangkat untuk diproses. Skrip akan keluar.")
            exit()
        
        print(f"Memulai akuisisi data dari {len(devices)} perangkat setiap {POLL_INTERVAL_SECONDS} detik...")
        
        while True:
            threads = []
            print(f"--- Memulai siklus polling {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
            for device in devices:
                # Memberikan write_api yang sama ke semua thread karena sudah SYNCHRONOUS
                thread = threading.Thread(target=process_single_device, args=(device, write_api, INFLUX_BUCKET, INFLUX_ORG))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join() # Tunggu semua thread selesai untuk siklus ini
            
            print(f"--- Siklus polling selesai. Menunggu {POLL_INTERVAL_SECONDS} detik... ---")
            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nSkrip akuisisi dihentikan oleh pengguna.")
    except Exception as e:
        print(f"Error utama dalam skrip: {e}")
    finally:
        if client:
            client.close()
            print("Koneksi InfluxDB ditutup.")