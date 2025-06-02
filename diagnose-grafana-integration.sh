#!/bin/bash

# Skrip untuk mendiagnosa koneksi Grafana dari web-react container

echo "==== Diagnosa Integrasi Grafana di Web-React ===="

# Cek status container
echo -e "\n[1] Status Container:"
docker-compose ps grafana web-react

# Cek konfigurasi variabel lingkungan di container web-react
echo -e "\n[2] Variabel Lingkungan Web-React:"
docker-compose exec web-react env | grep -E "REACT_APP_GRAFANA|NODE_ENV" || echo "Tidak ditemukan variabel GRAFANA"

# Cek koneksi jaringan docker
echo -e "\n[3] Jaringan Docker:"
docker network ls
echo -e "\nDetail Jaringan app_network:"
docker network inspect digitaltwin_app_network | grep -A 20 "Containers"

# Cek koneksi dari web-react ke grafana
echo -e "\n[4] Tes Koneksi Web-React ke Grafana:"
echo "Via HTTP (port 3000):"
docker-compose exec web-react wget -q -O- --timeout=5 --tries=1 http://grafana:3000/api/health || echo "Koneksi gagal"

# Cek akses URL Grafana secara langsung
echo -e "\n[5] Tes Akses URL Grafana Langsung:"
GRAFANA_URL="http://10.13.0.4:3001/d/7d1a6a29-626f-4f4d-a997-e7d0a7c3f872/f2?orgId=1&var-location=F2"
echo "URL: $GRAFANA_URL"
curl -s -I "$GRAFANA_URL" | head -n 1 || echo "Koneksi gagal"

# Cek konfigurasi Nginx di web-react
echo -e "\n[6] Konfigurasi Nginx di Web-React:"
docker-compose exec web-react cat /etc/nginx/conf.d/default.conf | grep -A 15 "/grafana"

echo -e "\n==== Selesai ===="
