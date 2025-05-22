#!/bin/bash

# Script untuk memulai aplikasi Digital Twin dengan pengaturan port dinamis
# Usage: ./start-dynamic.sh [--api-key YOUR_API_KEY] [--dev]

# Pastikan script dijalankan dari direktori root proyek
cd "$(dirname "$0")"

# Default values
DEV_MODE=true
API_KEY=${API_KEY:-development_key_for_testing}
FORCE_RESTART=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --prod)
      DEV_MODE=false
      shift
      ;;
    --force-restart)
      FORCE_RESTART=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./start-dynamic.sh [--api-key YOUR_API_KEY] [--prod] [--force-restart]"
      exit 1
      ;;
  esac
done

# Export API key for docker-compose
export API_KEY=$API_KEY

echo "=== Memulai aplikasi Digital Twin dengan port dinamis ==="
echo "=== Mode: $([ "$DEV_MODE" = true ] && echo "Development" || echo "Production") ==="

# Function to check if a port is in use
is_port_in_use() {
  local port=$1
  lsof -i:$port >/dev/null 2>&1
  return $?
}

# Find available port starting from base_port
find_available_port() {
  local base_port=$1
  local port=$base_port
  
  while is_port_in_use $port; do
    echo "⚠️ Port $port sudah digunakan, mencoba port berikutnya..."
    port=$((port + 1))
    # Jangan cari terlalu jauh
    if [ $port -gt $(($base_port + 20)) ]; then
      echo "❌ Tidak dapat menemukan port yang tersedia setelah mencoba 20 port."
      return 1
    fi
  done
  
  echo $port
  return 0
}

# Check if we should kill existing processes on port 3003 (React)
if [ "$FORCE_RESTART" = true ]; then
  echo "=== Memaksa restart: Menghentikan proses pada port 3003 ==="
  ./check-ports.sh --kill --port 3003
fi

# Find available port for React app
REACT_PORT=$(find_available_port 3003)
if [ $? -ne 0 ]; then
  echo "❌ Gagal menemukan port yang tersedia untuk aplikasi React."
  exit 1
fi

# Check API status
API_PORT=8002
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$API_PORT/health" 2>/dev/null || echo "Failed")

if [ "$API_STATUS" = "200" ]; then
  echo "✅ API terdeteksi berjalan di http://localhost:$API_PORT dan merespon dengan baik."
else
  echo "⚠️ API tidak terdeteksi di port $API_PORT atau tidak merespon dengan benar."
  echo "   Sebaiknya jalankan API terlebih dahulu dengan: python api.py"
  echo "   Melanjutkan memulai React app, tapi sebagian fitur mungkin tidak berfungsi."
fi

echo "=== Menjalankan webpack dev server dengan port dinamis... ==="
echo "=== Aplikasi akan berjalan di http://localhost:$REACT_PORT ==="

cd web-react

# Create .env.local file with proper configuration
cat > .env.local << EOL
REACT_APP_API_URL=http://localhost:$API_PORT
REACT_APP_API_KEY=$API_KEY
REACT_APP_PORT=$REACT_PORT
EOL

# Ensure node_modules exists
if [ ! -d "node_modules" ]; then
  echo "Menginstall dependencies React..."
  npm install
fi

# Run the app with the selected port
if [ "$REACT_PORT" -eq 3003 ]; then
  npm run start:3003
else
  npm start -- --port $REACT_PORT
fi
