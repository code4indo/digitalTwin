#!/bin/bash

# Script untuk membangun dan men-deploy container React dengan integrasi Grafana
# Usage: ./deploy-react-container.sh [--rebuild]

REBUILD=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --rebuild)
      REBUILD=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./deploy-react-container.sh [--rebuild]"
      exit 1
      ;;
  esac
done

echo "=== Digital Twin React Container Deployment ==="

# Periksa apakah docker dan docker-compose terinstall
if ! command -v docker &> /dev/null; then
  echo "❌ Docker tidak terinstall"
  echo "Silakan install Docker terlebih dahulu"
  exit 1
fi

if ! command -v docker compose &> /dev/null; then
  echo "❌ docker compose tidak terinstall"
  echo "Silakan install Docker Compose terlebih dahulu"
  exit 1
fi

# Periksa apakah berada di direktori root project
if [ ! -f "docker-compose.yml" ]; then
  echo "❌ File docker-compose.yml tidak ditemukan"
  echo "Pastikan menjalankan script ini dari direktori root project"
  exit 1
fi

# Periksa port yang digunakan oleh layanan
./check-ports.sh --port 3003
PORT_STATUS=$?

if [ $PORT_STATUS -ne 0 ]; then
  echo "⚠️ Port 3003 sudah digunakan oleh proses lain"
  read -p "Apakah Anda ingin membebaskan port 3003? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./check-ports.sh --kill --port 3003
  else
    echo "Deployment dibatalkan"
    exit 1
  fi
fi

# Export environment variables dari .env.local jika ada
if [ -f "web-react/.env.local" ]; then
  echo "🔄 Menggunakan konfigurasi dari .env.local..."
  export $(grep -v '^#' web-react/.env.local | xargs)
fi

# Validasi konfigurasi Grafana
if [ -z "$REACT_APP_GRAFANA_DASHBOARD_ID" ]; then
  echo "⚠️ REACT_APP_GRAFANA_DASHBOARD_ID tidak dikonfigurasi!"
  read -p "Masukkan Dashboard ID Grafana: " GRAFANA_DASHBOARD_ID
  export GRAFANA_DASHBOARD_ID
else
  export GRAFANA_DASHBOARD_ID=$REACT_APP_GRAFANA_DASHBOARD_ID
fi

if [ -z "$REACT_APP_GRAFANA_PANEL_ID" ]; then
  echo "⚠️ REACT_APP_GRAFANA_PANEL_ID tidak dikonfigurasi!"
  read -p "Masukkan Panel ID Grafana: " GRAFANA_PANEL_ID
  export GRAFANA_PANEL_ID
else
  export GRAFANA_PANEL_ID=$REACT_APP_GRAFANA_PANEL_ID
fi

# Periksa konfigurasi Grafana
echo "🔍 Memeriksa konfigurasi Grafana..."
./check-grafana-integration.sh
GRAFANA_STATUS=$?

if [ $GRAFANA_STATUS -ne 0 ]; then
  echo "⚠️ Integrasi Grafana mungkin bermasalah"
  read -p "Lanjutkan deployment? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment dibatalkan"
    exit 1
  fi
fi

# Rebuild container jika diminta
if [ "$REBUILD" = true ]; then
  echo "🔄 Membangun ulang container React..."
  docker compose build web-react
fi

# Deploy container
echo "🚀 Menjalankan container React..."
docker compose up -d web-react

# Periksa status container
echo "📊 Status container:"
docker compose ps web-react

echo -e "\n✅ Deployment selesai!"
echo "React UI tersedia di: http://localhost:3003"
echo "Grafana tersedia di: http://localhost:3001"
echo "API tersedia di: http://localhost:8002"
echo
echo "Untuk memeriksa logs:"
echo "  docker compose logs -f web-react"
