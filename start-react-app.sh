#!/bin/bash

# Script untuk membangun dan memulai aplikasi React dengan Docker
# Usage: ./start-react-app.sh [--api-key YOUR_API_KEY] [--dev]

# Pastikan script dijalankan dari direktori root proyek
cd "$(dirname "$0")"

# Default values
DEV_MODE=false
API_KEY=${API_KEY:-development_key_for_testing}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --dev)
      DEV_MODE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./start-react-app.sh [--api-key YOUR_API_KEY] [--dev]"
      exit 1
      ;;
  esac
done

# Export API key for docker-compose
export API_KEY=$API_KEY

echo "=== Membangun dan menjalankan aplikasi React Digital Twin ==="
echo "=== Mode: $([ "$DEV_MODE" = true ] && echo "Development" || echo "Production") ==="

# Check if Docker is available
DOCKER_AVAILABLE=false
if command -v docker &> /dev/null && docker info &> /dev/null; then
  DOCKER_AVAILABLE=true
else
  echo "⚠️ Docker tidak tersedia atau Anda tidak memiliki izin untuk menggunakan Docker."
  echo "   Beberapa layanan seperti InfluxDB dan API container mungkin tidak akan berjalan."
  
  # Jika dalam mode production tapi Docker tidak tersedia, keluar dengan error
  if [ "$DEV_MODE" = false ]; then
    echo "❌ Mode production membutuhkan Docker. Silakan jalankan dengan '--dev' atau perbaiki masalah Docker."
    exit 1
  fi
fi

# Function to check if a port is in use
is_port_in_use() {
  local port=$1
  if command -v nc &> /dev/null; then
    nc -z localhost $port &>/dev/null
    return $?
  elif command -v lsof &> /dev/null; then
    lsof -i:$port &>/dev/null
    return $?
  else
    # Fallback to direct /dev/tcp check in bash
    (echo >/dev/tcp/localhost/$port) &>/dev/null
    return $?
  fi
}

# Find available port starting from base_port
find_available_port() {
  local base_port=$1
  local port=$base_port
  
  while is_port_in_use $port; do
    echo "⚠️ Port $port sudah digunakan, mencoba port berikutnya..."
    port=$((port + 1))
  done
  
  echo $port
}

# Command to run
if [ "$DEV_MODE" = true ]; then
  # Development mode - buat container terpisah untuk development
  if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "=== Menjalankan API dan InfluxDB dengan Docker ==="
    docker-compose -f docker-compose.yml up -d --build api influxdb
    API_RUNNING=$?
    
    if [ $API_RUNNING -ne 0 ]; then
      echo "⚠️ Gagal menjalankan container Docker. API dan InfluxDB mungkin tidak tersedia."
      echo "   Aplikasi React akan tetap dijalankan secara lokal."
    else
      echo "✅ API dan InfluxDB sedang berjalan di Docker"
    fi
  else
    echo "⚠️ Memeriksa apakah API sudah berjalan secara lokal..."
    if ! curl -s http://localhost:8002/health > /dev/null; then
      echo "❌ API tidak terdeteksi di http://localhost:8002"
      echo "   Anda mungkin perlu menjalankan API secara manual: python api.py"
    else
      echo "✅ API terdeteksi berjalan di http://localhost:8002"
    fi
  fi
  
  echo "=== Menjalankan React dalam mode development lokal ==="
  
  # Jalankan React dalam mode development
  cd web-react
  echo "REACT_APP_API_URL=http://localhost:8002" > .env.local
  echo "REACT_APP_API_KEY=$API_KEY" >> .env.local
  npm install
  
  # Cari port yang tersedia jika 3003 sudah digunakan
  REACT_PORT=$(find_available_port 3003)
  
  if [ "$REACT_PORT" -ne 3003 ]; then
    echo "⚠️ Port 3003 sudah digunakan. Menggunakan port $REACT_PORT sebagai gantinya."
    echo "=== Aplikasi React Digital Twin akan berjalan di http://localhost:$REACT_PORT ==="
    npm run start -- --port $REACT_PORT
  else
    echo "=== Aplikasi React Digital Twin akan berjalan di http://localhost:3003 ==="
    npm run start:3003
  fi
else
  # Production mode - gunakan Docker untuk semuanya
  if [ "$DOCKER_AVAILABLE" = true ]; then
    docker-compose up -d --build web-react api influxdb
    
    echo "=== Aplikasi React Digital Twin berjalan di http://localhost:3003 ==="
    echo "=== API tersedia di http://localhost:8002 ==="
    echo "=== Untuk melihat log, gunakan: docker-compose logs -f web-react ==="
  else
    echo "❌ Mode production membutuhkan Docker. Docker tidak tersedia."
    exit 1
  fi
fi
