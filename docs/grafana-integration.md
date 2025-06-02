# Integrasi Grafana dengan Digital Twin

Dokumen ini menjelaskan cara mengintegrasikan dashboard Grafana ke dalam aplikasi Digital Twin.

## Persiapan

### 1. Konfigurasi Grafana

1. **Aktifkan embedding di Grafana**:
   
   Edit file konfigurasi Grafana (biasanya di `/etc/grafana/grafana.ini`) dan pastikan setting berikut sudah aktif:
   ```ini
   [security]
   allow_embedding = true
   ```

2. **Buat Variabel `location` di Grafana**:
   
   - Buka dashboard Grafana yang ingin diintegrasikan
   - Klik ikon roda gigi (⚙️) untuk masuk ke pengaturan dashboard
   - Pilih tab "Variables"
   - Klik "Add variable"
   - Isi formulir:
     - Name: `location`
     - Type: "Query"
     - Data source: InfluxDB Anda
     - Query (Flux):
       ```
       import "influxdata/influxdb/schema"
  
       schema.measurementTagValues(
         bucket: "sensor_data_primary",
         measurement: "sensor_reading",
         tag: "location"
       )
       ```
   - Klik "Add"

### 2. Dapatkan ID Dashboard dan Panel ID

1. **Untuk mendapatkan Dashboard ID**:
   - Buka dashboard Grafana yang ingin digunakan
   - Perhatikan URL browser:
     `http://your-grafana-url/d/AbCdEfGhI/dashboard-name`
   - Di sini, `AbCdEfGhI` adalah Dashboard ID Anda

2. **Untuk mendapatkan Panel ID**:
   - Klik pada judul panel untuk membuka menu edit panel
   - Perhatikan URL yang sekarang berisi `editPanel=12`
   - Di sini, `12` adalah Panel ID Anda

### 3. Konfigurasi Aplikasi React

1. **Salin template .env.local**:
   ```bash
   cp .env.local.template .env.local
   ```

2. **Edit .env.local** dan masukkan nilai-nilai yang sesuai:
   ```
   REACT_APP_GRAFANA_URL=http://localhost:3000
   REACT_APP_GRAFANA_DASHBOARD_ID=AbCdEfGhI
   REACT_APP_GRAFANA_PANEL_ID=12
   ```

## Penggunaan

Komponen `RoomEnvironmentalChart` akan secara otomatis menampilkan data dari Grafana untuk ruangan yang dipilih. Komponen ini menggunakan parameter `location` dari Grafana untuk memfilter data sesuai dengan ruangan yang dipilih di aplikasi React.

## Troubleshooting

1. **Chart tidak muncul**: 
   - Pastikan variabel lingkungan sudah diatur dengan benar
   - Periksa apakah Grafana dapat diakses dari browser
   - Periksa browser console untuk error

2. **Data tidak difilter sesuai ruangan**:
   - Pastikan variabel `location` di Grafana sudah dikonfigurasi dengan benar
   - Verifikasi bahwa nilai `roomId` yang dikirim ke komponen chart cocok dengan nilai yang ada di database

3. **Masalah autentikasi**:
   - Jika menggunakan Grafana yang memerlukan login, tambahkan token API Grafana di `.env.local`:
     ```
     REACT_APP_GRAFANA_AUTH_TOKEN=your-auth-token
     ```
   - Update komponen `RoomEnvironmentalChart` untuk menggunakan token tersebut

# Troubleshooting: Error "Failed to configure Grafana URL"

## 🔍 Analisis Masalah

Error "Failed to configure Grafana URL" dapat terjadi karena beberapa penyebab:

### 1. **Missing Environment Variables pada Build Time**
- React membutuhkan environment variables saat build untuk embed ke bundle
- Environment variables yang hanya di-set pada runtime tidak akan tersedia

**Solusi:**
```dockerfile
# Di Dockerfile.react - pastikan ARG dan ENV di-set sebelum npm run build
ARG REACT_APP_GRAFANA_URL=/grafana
ARG REACT_APP_GRAFANA_DASHBOARD_ID=environmental-dashboard
ARG REACT_APP_GRAFANA_PANEL_ID=2

ENV REACT_APP_GRAFANA_URL=${REACT_APP_GRAFANA_URL}
ENV REACT_APP_GRAFANA_DASHBOARD_ID=${REACT_APP_GRAFANA_DASHBOARD_ID}
ENV REACT_APP_GRAFANA_PANEL_ID=${REACT_APP_GRAFANA_PANEL_ID}

RUN npm run build
```

### 2. **Dashboard ID atau Panel ID Tidak Valid**
- Dashboard dengan ID yang dikonfigurasi belum dibuat di Grafana
- Panel ID tidak sesuai dengan panel yang ada

**Solusi:**
- Gunakan script `setup-grafana-dashboard.sh` untuk membuat dashboard otomatis
- Atau buat dashboard manual dan update environment variables

### 3. **Konfigurasi Proxy Issues**
- Nginx proxy tidak dikonfigurasi dengan benar untuk Grafana
- Missing headers untuk iframe embedding

**Solusi:**
```nginx
# Di nginx.conf
location /grafana/ {
    proxy_pass http://grafana:3000/;
    # Headers khusus untuk iframe embedding
    proxy_hide_header X-Frame-Options;
    proxy_set_header X-Frame-Options "SAMEORIGIN";
    # Grafana subpath configuration
    proxy_set_header X-Forwarded-Prefix /grafana;
}
```

### 4. **X-Frame-Options Header Conflict**
- Grafana default mengirim `X-Frame-Options: deny`
- Ini mencegah iframe embedding

**Solusi:**
```yaml
# Di docker-compose.yml untuk service grafana
environment:
  - GF_SECURITY_ALLOW_EMBEDDING=true
  - GF_SECURITY_COOKIE_SAMESITE=disabled
  - GF_SERVER_ROOT_URL=http://localhost:3003/grafana/
  - GF_SERVER_SERVE_FROM_SUB_PATH=true
```

### 5. **Improved Error Handling**
Update komponen React untuk memberikan informasi debug yang lebih baik:

```javascript
// Di RoomEnvironmentalChart.js
console.log('Grafana Config:', { baseUrl, dashboardId, panelId, roomId });

if (!dashboardId || !panelId) {
  console.error('Missing Grafana configuration:', { dashboardId, panelId });
  setError('Konfigurasi Grafana tidak lengkap. Dashboard atau Panel ID tidak ditemukan.');
  return;
}
```

## 🛠️ Langkah-langkah Perbaikan

1. **Stop semua container:**
   ```bash
   docker-compose down
   ```

2. **Rebuild dengan konfigurasi yang diperbaiki:**
   ```bash
   docker-compose up -d --build
   ```

3. **Setup dashboard Grafana:**
   ```bash
   ./setup-grafana-dashboard.sh
   ```

4. **Verifikasi:**
   - Akses http://localhost:3003 untuk web app
   - Akses http://localhost:3001 untuk Grafana langsung
   - Akses http://localhost:3003/grafana untuk Grafana via proxy

## 🔧 Quick Fix Commands

```bash
# Restart dengan build ulang
docker-compose down && docker-compose up -d --build

# Setup dashboard otomatis
chmod +x setup-grafana-dashboard.sh && ./setup-grafana-dashboard.sh

# Check environment variables dalam container
docker exec web_react_service env | grep REACT_APP_GRAFANA

# Test proxy Grafana
curl -I http://localhost:3003/grafana/
```

## ✅ Verifikasi Perbaikan

1. **Environment Variables ter-embed:**
   ```bash
   docker exec web_react_service grep -o "REACT_APP_GRAFANA[^\"]*" /usr/share/nginx/html/bundle.js
   ```

2. **Console logs di browser:**
   - Buka Developer Tools → Console
   - Cari log "Grafana Config:" untuk melihat konfigurasi
   - Cari log "Generated Grafana URL:" untuk melihat URL yang dibuat

3. **Dashboard accessibility:**
   - Login ke Grafana: http://localhost:3001
   - Username: admin, Password: admin123
   - Cek dashboard "Environmental Monitoring"

## Integrasi Grafana dalam Lingkungan Container

### Docker Setup:

1. **Konfigurasi Container Grafana**
   - Grafana berjalan pada port 3001 (dipetakan dari port 3000 internal container)
   - Data persisten disimpan pada volume `grafana_data_volume`
   - Didefinisikan dalam `docker-compose.yml`:
   
   ```yaml
   grafana:
     image: grafana/grafana-oss:latest
     container_name: grafana_service
     restart: unless-stopped
     ports:
       - "3001:3000"
     volumes:
       - grafana_data_volume:/var/lib/grafana
     depends_on:
       - influxdb
     networks:
       - app_network
   ```

2. **Konfigurasi Proxy Nginx untuk Grafana**
   - Container React menggunakan Nginx untuk meng-proxy permintaan ke Grafana
   - Konfigurasi dalam `nginx.conf`:
   
   ```
   location /grafana/ {
       proxy_pass http://grafana:3000/;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection 'upgrade';
       proxy_set_header Host $host;
       proxy_cache_bypass $http_upgrade;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   }
   ```

3. **Komunikasi Antar Container**
   - Client (browser) mengakses Grafana via rute proxy `/grafana`
   - Container React mengakses Grafana via nama layanan Docker `http://grafana:3000`
   - Semua container berada di dalam jaringan Docker `app_network`

### Environment Variables dalam Container:

1. **Variabel Lingkungan untuk Container React**
   - Definisi dalam `docker-compose.yml`:
   
   ```yaml
   web-react:
     environment:
       - REACT_APP_GRAFANA_URL=/grafana
       - REACT_APP_GRAFANA_DASHBOARD_ID=${GRAFANA_DASHBOARD_ID}
       - REACT_APP_GRAFANA_PANEL_ID=${GRAFANA_PANEL_ID}
   ```

2. **Build Arguments**
   - Definisi dalam `docker-compose.yml`:
   
   ```yaml
   web-react:
     build:
       args:
         - REACT_APP_GRAFANA_URL=http://grafana:3000
         - REACT_APP_GRAFANA_DASHBOARD_ID=${GRAFANA_DASHBOARD_ID}
         - REACT_APP_GRAFANA_PANEL_ID=${GRAFANA_PANEL_ID}
   ```

### Langkah-langkah Deployment:

1. **Persiapkan Konfigurasi**
   - Salin `.env.local.template` ke `.env.local` dan isi dengan nilai yang sesuai
   - Dashboard ID dan Panel ID harus dikonfigurasi dengan benar

2. **Build dan Deploy Container**
   ```bash
   ./deploy-react-container.sh --rebuild
   ```

3. **Verifikasi Integrasi**
   - Akses aplikasi React: `http://localhost:3003`
   - Akses Grafana langsung: `http://localhost:3001`
   - Uji komponen `RoomEnvironmentalChart` dengan memilih ruangan

4. **Troubleshooting**
   - Periksa logs container: `docker compose logs web-react`
   - Periksa logs Grafana: `docker compose logs grafana`
   - Gunakan script `check-grafana-integration.sh` untuk diagnosis
