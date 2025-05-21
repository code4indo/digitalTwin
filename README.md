# Digital Twin Sistem Manajemen Iklim Mikro Gedung Arsip

Proyek ini mengembangkan sistem digital twin untuk manajemen iklim mikro di gedung arsip, mengintegrasikan data sensor internal, data cuaca eksternal BMKG, analisis prediktif, dan visualisasi interaktif.

## Tentang Proyek

Proyek ini bertujuan untuk mengembangkan sistem cerdas yang mengelola iklim mikro di gedung arsip dengan mengintegrasikan data dari:
- Sensor internal (suhu dan kelembapan) dari berbagai ruangan di gedung
- Data cuaca eksternal dari API BMKG
- Model machine learning untuk prediksi kondisi masa depan
- Visualisasi digital twin untuk monitoring dan kontrol

## Komponen Utama

1. **Pengumpulan Data**
   - `acquire_device_data.py` - Script untuk mengakuisisi data dari perangkat IoT
   - `telegraf.conf` - Konfigurasi Telegraf untuk pengumpulan data sensor
   - `bmkg_data_collector.py` - Pengumpul data cuaca dari API BMKG

2. **Penyimpanan Data**
   - InfluxDB sebagai time-series database

3. **API dan Backend**
   - `api.py` - REST API untuk mengakses data sensor

4. **Web Interface Digital Twin**
   - Visualisasi 3D bangunan menggunakan Three.js
   - Dashboard monitoring kondisi real-time
   - Sistem rekomendasi dan otomasi
   - Analisis prediktif menggunakan machine learning
   - Frontend berbasis React

## Cara Menggunakan

### Pengumpulan Data IoT

Data sensor dikumpulkan dari perangkat dengan format: `kelembapan#suhu#id_device`  
Contoh: `46#22.20#2D303D`, di mana:
- `46` adalah kelembapan (%)
- `22.20` adalah suhu (°C)
- `2D303D` adalah ID device

### Menjalankan Server API

```bash
python api.py
```

### Frontend React

Frontend aplikasi dibangun menggunakan React.js, Three.js, dan Chart.js untuk visualisasi data.

#### Menjalankan Frontend dalam Mode Development

```bash
cd web-react
npm install
npm start
```

#### Build Frontend untuk Production

```bash
cd web-react
npm install
npm run build
```

Atau gunakan script deploy yang telah disediakan:

```bash
./deploy-react.sh
```

Script ini akan membangun aplikasi React dan mendeploy hasilnya ke folder `web` yang akan diserve oleh Nginx atau web server lainnya.

### Menjalankan dengan Docker Compose

Untuk menjalankan seluruh sistem (database, API, web server, data collector) dalam container Docker:

```bash
docker-compose up -d
```

Setelah semua container berjalan:
1. Akses web interface di `http://localhost:80`
2. Akses API di `http://localhost:8002`
3. Akses Grafana dashboard di `http://localhost:3001` (login dengan admin_user/admin_password)
4. Akses InfluxDB di `http://localhost:8086`

### Panduan Lengkap Instalasi dan Konfigurasi

#### Prasyarat
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 16+](https://nodejs.org/)
- [Docker](https://www.docker.com/get-started) dan [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)

#### Instalasi Manual

1. **Clone repositori**
   ```bash
   git clone https://github.com/your-username/digitalTwin.git
   cd digitalTwin
   ```

2. **Setup lingkungan Python**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Linux/macOS
   # atau
   venv\Scripts\activate     # Untuk Windows
   pip install -r requirements.txt
   ```
   
   Alternatif jika menggunakan Poetry:
   ```bash
   poetry install
   poetry shell
   ```

3. **Setup frontend React**
   ```bash
   cd web-react
   npm install
   ```

4. **Konfigurasi environment**
   - Salin `.env.example` ke `.env` dan sesuaikan nilai-nilainya
   ```bash
   cp .env.example .env
   ```

#### Menjalankan Aplikasi Secara Terpisah

1. **Jalankan backend API**
   ```bash
   python api.py
   # atau
   uvicorn api:app --reload --port 8002
   ```

2. **Jalankan frontend React (mode development)**
   ```bash
   cd web-react
   npm start
   ```

3. **Jalankan collector data BMKG**
   ```bash
   python bmkg_data_collector.py
   ```

## Integrasi Data dengan Telegraf

Telegraf dikonfigurasi untuk mengumpulkan data dari:
1. Sensor internal melalui HTTP
2. Data cuaca eksternal dari API BMKG

## Fitur Digital Twin

- **Visualisasi Gedung** - Model 3D interaktif untuk melihat kondisi setiap ruangan
- **Monitoring Real-time** - Dashboard yang menampilkan suhu, kelembapan, dan status perangkat
- **Analisis Prediktif** - Prediksi kondisi iklim mikro untuk beberapa jam ke depan
- **Rekomendasi Otomatis** - Saran untuk menjaga kondisi optimal bagi preservasi arsip
- **Kontrol Sistem** - Antarmuka untuk mengontrol perangkat HVAC jika diintegrasikan

## Struktur Aplikasi React

Frontend React memiliki struktur sebagai berikut:

```
web-react/
├── public/                # Aset statis
├── src/
│   ├── components/        # Komponen React
│   │   ├── BuildingModel.js    # Visualisasi 3D gedung
│   │   ├── EnvironmentalStatus.js   # Status lingkungan
│   │   ├── AlertsPanel.js     # Panel peringatan
│   │   ├── TrendAnalysis.js   # Analisis tren data
│   │   └── PredictionsChart.js  # Grafik prediksi
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Fungsi utilitas
│   │   └── api.js         # Client API
│   ├── App.js             # Komponen utama
│   ├── App.css            # Style utama
│   └── index.js           # Entry point
├── webpack.config.js      # Konfigurasi webpack
└── package.json           # Dependensi dan script
```

## Aplikasi Web React

### Menjalankan Aplikasi Web React

Aplikasi web berbasis React dapat dijalankan dengan dua mode:

#### Mode 1: Menggunakan Docker Container

```bash
# Menjalankan aplikasi React dalam container Docker
./start-react-app.sh

# Dengan API key kustom
./start-react-app.sh --api-key your_api_key_here
```

#### Mode 2: Development Mode

```bash
# Menjalankan API dan database di container, tapi React dalam mode development lokal
./start-react-app.sh --dev
```

### Memeriksa Status Sistem

Gunakan script pemeriksaan status sistem untuk memastikan semua komponen berjalan dengan baik:

```bash
./check-system-status.sh
```

### Mengakses Aplikasi

- Aplikasi Web React: [http://localhost:3003](http://localhost:3003)
- API FastAPI: [http://localhost:8002/docs](http://localhost:8002/docs)
- InfluxDB: [http://localhost:8086](http://localhost:8086)
- Grafana Dashboard: [http://localhost:3001](http://localhost:3001)

### Fitur Aplikasi Web

1. **Dashboard Interaktif**
   - Visualisasi kondisi real-time dari seluruh gedung
   - Pemantauan suhu dan kelembapan per ruangan
   - Indikator status dan peringatan

2. **Representasi Digital Twin**
   - Model 3D gedung dengan overlay data sensor
   - Navigasi interaktif antar ruangan
   - Visualisasi distribusi suhu dan kelembapan

3. **Analisis Prediktif**
   - Prakiraan kondisi iklim mikro ke depan
   - Identifikasi potensi kondisi berbahaya
   - Rekomendasi untuk optimasi

4. **Kontrol & Otomatisasi**
   - Antarmuka pengaturan parameter lingkungan
   - Penjadwalan otomatis untuk sistem HVAC
   - Riwayat perubahan dan efek

## Pengembangan Selanjutnya

- Integrasi dengan sistem otomasi gedung (BMS)
- Pengembangan model ML yang lebih akurat untuk prediksi kondisi lingkungan
- Ekspansi visualisasi digital twin dengan detail ruangan yang lebih kompleks
- Implementasi feedback loop untuk pembelajaran berkelanjutan
- Implementasi autentikasi dan pengelolaan pengguna dengan berbagai tingkat akses
- Dashboard admin untuk konfigurasi sistem dan manajemen perangkat
- Integrasi dengan sistem kontrol otomatis HVAC untuk regulasi lingkungan otomatis
- Penambahan fitur notifikasi (email, SMS, mobile push) untuk kondisi kritis

## Kontribusi

Kontribusi selalu diterima! Untuk berkontribusi pada proyek ini:

1. Fork repositori
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

## Lisensi

Proyek ini dilisensikan di bawah lisensi MIT - lihat file [LICENSE](LICENSE) untuk detail.

## Kontak

Nama Tim Proyek - [@twitter_handle](https://twitter.com/twitter_handle) - email@example.com

Link Proyek: [https://github.com/yourusername/digitalTwin](https://github.com/yourusername/digitalTwin)

## Pemecahan Masalah (Troubleshooting)

### Masalah Koneksi dengan API

Jika frontend tidak dapat menghubungi API:
1. Pastikan API server berjalan di port 8002
2. Periksa CORS settings di `api.py`
3. Periksa konfigurasi proxy di `webpack.config.js`

### Masalah dengan Docker

Jika container Docker tidak berjalan dengan benar:
1. Periksa logs dengan `docker-compose logs -f [service_name]`
2. Pastikan semua port yang diperlukan tidak digunakan oleh aplikasi lain
3. Restart services dengan `docker-compose restart [service_name]`

### Masalah dengan Data Sensor

Jika data sensor tidak muncul:
1. Periksa koneksi ke InfluxDB dengan `python verify_influxdb_data.py`
2. Pastikan Telegraf berjalan dengan benar
3. Periksa `device_list.csv` untuk memastikan semua perangkat terdaftar

## FAQ

**Q: Bagaimana cara menambahkan sensor baru?**  
A: Tambahkan entri baru di file `device_list.csv` dengan format: `id_device,nama_ruangan,lantai,posisi_x,posisi_y`

**Q: Bagaimana cara mengubah interval pengambilan data BMKG?**  
A: Edit parameter `INTERVAL_MINUTES` di file `bmkg_data_collector.py`

**Q: Bagaimana cara mengakses API documentation?**  
A: Buka `http://localhost:8002/docs` setelah menjalankan API server

**Q: Bagaimana cara mengubah model 3D gedung?**  
A: Edit file `web-react/src/components/BuildingModel.js` untuk menyesuaikan model Three.js

**Q: Bagaimana cara mengubah kredensial default?**  
A: Edit file `.env` atau variabel environment di `docker-compose.yml`

## Endpoint API untuk Pemeriksaan Kesehatan Sistem

API menyediakan beberapa endpoint untuk memantau kesehatan sistem, berikut adalah endpoint utama yang tersedia:

### 1. Endpoint Kesehatan Sistem

- **URL**: `/system/health/`
- **Method**: GET
- **Deskripsi**: Menampilkan status kesehatan keseluruhan sistem, termasuk koneksi ke InfluxDB dan status perangkat
- **Memerlukan Autentikasi**: Ya (X-API-Key)
- **Response**: 
  ```json
  {
    "status": "Optimal|Good|Warning|Critical|No Devices Configured",
    "active_devices": 10,
    "total_devices": 12,
    "ratio_active_to_total": 0.8333,
    "influxdb_connection": "connected|disconnected"
  }
  ```
- **Catatan Status**:
  - **Optimal**: >90% perangkat aktif dan InfluxDB terhubung
  - **Good**: ≥75% perangkat aktif dan InfluxDB terhubung
  - **Warning**: ≥50% perangkat aktif atau InfluxDB tidak terhubung
  - **Critical**: <50% perangkat aktif
  - **No Devices Configured**: Tidak ada perangkat yang dikonfigurasi

### 2. Endpoint Daftar Perangkat

- **URL**: `/devices/`
- **Method**: GET
- **Deskripsi**: Menampilkan daftar semua perangkat yang terdaftar di sistem dengan lokasi terakhirnya
- **Memerlukan Autentikasi**: Ya (X-API-Key)
- **Response**: Array dari objek perangkat

### 3. Endpoint Data Sensor

- **URL**: `/data/`
- **Method**: GET
- **Deskripsi**: Mengambil data sensor dengan berbagai opsi filter dan agregasi
- **Parameter Query**: 
  - `start_time`: Waktu mulai (ISO format)
  - `end_time`: Waktu selesai (ISO format)
  - `device_ids`: Daftar ID perangkat
  - `locations`: Daftar lokasi
  - `fields`: Kolom data spesifik (suhu, kelembapan, dll)
  - `limit`: Jumlah maksimal data (default: 100)
  - `aggregate_window`: Jendela waktu agregasi (mis. "1h", "30m")
  - `aggregate_function`: Fungsi agregasi (mean, median, min, max, dll)
- **Memerlukan Autentikasi**: Ya (X-API-Key)
- **Response**: Array dari pengukuran sensor

### 4. Endpoint Status Perangkat

- **URL**: `/system/device_status/`
- **Method**: GET
- **Deskripsi**: Menampilkan daftar semua perangkat dengan status aktif atau tidak aktif berdasarkan pemeriksaan ping terakhir
- **Memerlukan Autentikasi**: Ya (X-API-Key)
- **Response**: 
  ```json
  {
    "devices": [
      {
        "ip_address": "10.6.0.13",
        "is_active": true,
        "last_checked": "2025-05-21T10:15:30.123456"
      },
      {
        "ip_address": "10.6.0.14",
        "is_active": false,
        "last_checked": "2025-05-21T10:15:30.123456"
      },
      ...
    ],
    "last_refresh_time": "2025-05-21T10:15:30.123456"
  }
  ```
- **Catatan**: Endpoint ini berguna untuk melihat status perangkat individual, yang tidak tersedia di endpoint `/system/health/`

## Menguji API dengan Postman

Untuk menguji API menggunakan Postman, ikuti langkah-langkah berikut:

### Persiapan

1. **Download dan Install Postman**:
   - Unduh Postman dari [postman.com](https://www.postman.com/downloads/)
   - Install dan buka aplikasinya

2. **Siapkan API Key**:
   - Dapatkan API Key yang valid dari file `.env` atau administrator sistem

### Menguji Endpoint Kesehatan Sistem

1. **Buat Request Baru**:
   - Klik tombol "New" dan pilih "HTTP Request"
   - Masukkan URL: `http://localhost:8002/system/health/`
   - Pilih metode: GET

2. **Tambahkan Header Autentikasi**:
   - Pilih tab "Headers"
   - Tambahkan key: `X-API-Key`
   - Tambahkan value: `[API_KEY_ANDA]` (ganti dengan API key yang valid)

3. **Kirim Request**:
   - Klik tombol "Send" dan lihat respons

### Menguji Endpoint Data Sensor

1. **Buat Request Baru**:
   - Masukkan URL: `http://localhost:8002/data/`
   - Pilih metode: GET

2. **Tambahkan Parameter Query**:
   - Pilih tab "Params"
   - Tambahkan parameter (key-value):
     - `start_time`: `2023-01-01T00:00:00Z` (sesuaikan tanggalnya)
     - `limit`: `10`
     - `aggregate_window`: `30m` (opsional)
     - `aggregate_function`: `mean` (opsional)

3. **Tambahkan Header Autentikasi**:
   - Seperti pada contoh sebelumnya

4. **Kirim Request**:
   - Klik tombol "Send" dan lihat respons

### Menggunakan Collection dan Environment

Untuk mempermudah pengujian rutin:

1. **Buat Environment**:
   - Klik "Environments" dan "New"
   - Tambahkan variabel:
     - `base_url`: `http://localhost:8002`
     - `api_key`: `[API_KEY_ANDA]`

2. **Buat Collection**:
   - Klik "Collections" dan "New Collection"
   - Beri nama "Digital Twin API"
   - Tambahkan request untuk setiap endpoint

3. **Gunakan Variabel Environment**:
   - Dalam request, gunakan `{{base_url}}/system/health/`
   - Dalam header, gunakan `{{api_key}}`

Dengan collection dan environment, Anda dapat dengan mudah menguji API di berbagai lingkungan (development, staging, production) cukup dengan mengganti nilai variabel environment.


perintah update container

sudo docker-compose up -d --build api

