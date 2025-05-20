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
   - Visualisasi 3D bangunan
   - Dashboard monitoring kondisi real-time
   - Sistem rekomendasi dan otomasi
   - Analisis prediktif menggunakan machine learning

## Cara Menggunakan

### Pengumpulan Data IoT

Data sensor dikumpulkan dari perangkat dengan format: `kelembapan#suhu#id_device`  
Contoh: `46#22.20#2D303D`, di mana:
- `46` adalah kelembapan (%)
- `22.20` adalah suhu (°C)
- `2D303D` adalah ID device

### Menjalankan Web Interface Digital Twin

1. Pastikan InfluxDB dan Telegraf berjalan
2. Jalankan server web interface:

```bash
python web_server.py
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

## Pengembangan Selanjutnya

- Integrasi dengan sistem otomasi gedung (BMS)
- Pengembangan model ML yang lebih akurat
- Ekspansi visualisasi digital twin
- Implementasi feedback loop untuk pembelajaran berkelanjutan 