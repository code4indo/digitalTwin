#!/bin/bash

# Script untuk memeriksa status API dan konektivitas sistem
# Usage: ./check-system-status.sh [--api-key YOUR_API_KEY]

API_KEY=${API_KEY:-development_key_for_testing}
API_URL=${API_URL:-http://localhost:8002}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --api-url)
      API_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./check-system-status.sh [--api-key YOUR_API_KEY] [--api-url http://your-api-url:8002]"
      exit 1
      ;;
  esac
done

echo "Memeriksa status sistem Digital Twin..."
echo "API URL: $API_URL"

# Fungsi untuk memeriksa status HTTP
check_http_status() {
  local url=$1
  local expected_status=$2
  local request_type=$3
  local status=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" $url)
  
  if [ "$status" -eq "$expected_status" ]; then
    echo "✅ $request_type OK (HTTP $status)"
    return 0
  else
    echo "❌ $request_type Tidak Berhasil (HTTP $status, diharapkan $expected_status)"
    return 1
  fi
}

# Cek status sistem
system_health_check() {
  echo -e "\n=== Memeriksa Endpoint Health ==="
  
  # Menyimpan respons di file temporary
  response_file=$(mktemp)
  curl -s -H "X-API-Key: $API_KEY" $API_URL/system/health/ > $response_file
  
  if [ $? -ne 0 ]; then
    echo "❌ Tidak dapat terhubung ke API"
    rm $response_file
    return 1
  fi

  http_status=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" $API_URL/system/health/)
  
  if [ "$http_status" -eq 200 ]; then
    echo "✅ Health Endpoint: OK (HTTP 200)"
    
    # Parse respons JSON
    status=$(grep -o '"status":"[^"]*"' $response_file | cut -d'"' -f4)
    active_devices=$(grep -o '"active_devices":[0-9]*' $response_file | cut -d':' -f2)
    total_devices=$(grep -o '"total_devices":[0-9]*' $response_file | cut -d':' -f2)
    ratio=$(grep -o '"ratio_active_to_total":[0-9.]*' $response_file | cut -d':' -f2)
    influxdb=$(grep -o '"influxdb_connection":"[^"]*"' $response_file | cut -d'"' -f4)
    
    echo "📊 Status Sistem: $status"
    echo "📱 Perangkat Aktif: $active_devices dari $total_devices (Rasio: $ratio)"
    echo "🗄️ Koneksi InfluxDB: $influxdb"
    
    # Periksa status lebih detail
    if [ "$influxdb" = "disconnected" ]; then
      echo "⚠️ PERINGATAN: InfluxDB tidak terhubung!"
    fi
    
    if [ "$status" = "Critical" ]; then
      echo "⚠️ PERINGATAN: Status sistem kritis!"
    elif [ "$status" = "Warning" ]; then
      echo "⚠️ PERINGATAN: Status sistem dalam status peringatan!"
    fi
  else
    echo "❌ Health Endpoint: Tidak Berhasil (HTTP $http_status)"
  fi
  
  rm $response_file
}

# Cek ketersediaan endpoint lain
endpoint_availability_check() {
  echo -e "\n=== Memeriksa Endpoint Lainnya ==="
  check_http_status "$API_URL/devices/" 200 "Endpoint Devices"
  check_http_status "$API_URL/data/?limit=1" 200 "Endpoint Data"
}

# Cek aplikasi React
react_app_check() {
  echo -e "\n=== Memeriksa Aplikasi React ==="
  local react_url="http://localhost:3003"
  local react_status=$(curl -s -o /dev/null -w "%{http_code}" $react_url)
  
  if [ "$react_status" -eq 200 ]; then
    echo "✅ Aplikasi React: OK (HTTP 200)"
  else
    echo "❌ Aplikasi React: Tidak Berhasil (HTTP $react_status)"
    echo "   Pastikan container web-react sedang berjalan."
  fi
}

# Jalankan semua pemeriksaan
system_health_check
endpoint_availability_check
react_app_check

echo -e "\n=== Pemeriksaan Selesai ==="
