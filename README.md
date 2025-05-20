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

3. Buka browser dan akses `http://localhost:8000`

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

## Pengembangan Selanjutnya

- Integrasi dengan sistem otomasi gedung (BMS)
- Pengembangan model ML yang lebih akurat
- Ekspansi visualisasi digital twin
- Implementasi feedback loop untuk pembelajaran berkelanjutan
- Implementasi autentikasi dan pengelolaan pengguna
- Dashboard admin untuk konfigurasi sistem
- Integrasi dengan sistem kontrol otomatis (HVAC)
- Pengembangan model machine learning yang lebih akurat