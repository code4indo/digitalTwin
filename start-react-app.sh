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

# Command to run
if [ "$DEV_MODE" = true ]; then
  # Development mode - buat container terpisah untuk development
  docker-compose -f docker-compose.yml up -d --build api influxdb
  
  echo "=== API dan InfluxDB sedang berjalan ==="
  echo "=== Menjalankan React dalam mode development lokal ==="
  
  # Jalankan React dalam mode development
  cd web-react
  echo "REACT_APP_API_URL=http://localhost:8002" > .env.local
  echo "REACT_APP_API_KEY=$API_KEY" >> .env.local
  npm install
  npm run start:3003
else
  # Production mode - gunakan Docker untuk semuanya
  docker-compose up -d --build web-react api influxdb
  
  echo "=== Aplikasi React Digital Twin berjalan di http://localhost:3003 ==="
  echo "=== API tersedia di http://localhost:8002 ==="
  echo "=== Untuk melihat log, gunakan: docker-compose logs -f web-react ==="
fi
