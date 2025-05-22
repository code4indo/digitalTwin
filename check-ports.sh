#!/bin/bash

# Script untuk memeriksa dan mengelola port yang sedang digunakan
# Usage: ./check-ports.sh [--kill] [--port PORT_NUMBER]

KILL_PROCESSES=false
PORT_TO_CHECK=3003

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --kill)
      KILL_PROCESSES=true
      shift
      ;;
    --port)
      PORT_TO_CHECK="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./check-ports.sh [--kill] [--port PORT_NUMBER]"
      exit 1
      ;;
  esac
done

echo "=== Memeriksa port yang sedang digunakan ==="

# Periksa port yang ditentukan
echo "Memeriksa port $PORT_TO_CHECK:"
PORT_STATUS=$(lsof -i:$PORT_TO_CHECK -t 2>/dev/null)

if [ -z "$PORT_STATUS" ]; then
  echo "✅ Port $PORT_TO_CHECK tersedia"
else
  echo "⚠️ Port $PORT_TO_CHECK sedang digunakan oleh proses berikut:"
  for PID in $PORT_STATUS; do
    PROCESS_INFO=$(ps -p $PID -o pid,user,command | tail -n +2)
    echo "PID: $PID - $PROCESS_INFO"
  done
  
  if [ "$KILL_PROCESSES" = true ]; then
    echo "Mencoba menghentikan proses..."
    for PID in $PORT_STATUS; do
      echo "Menghentikan proses $PID..."
      kill -15 $PID
      sleep 1
      
      # Periksa apakah proses masih berjalan
      if ps -p $PID >/dev/null 2>&1; then
        echo "Proses $PID masih berjalan, menggunakan force kill..."
        kill -9 $PID
      fi
    done
    
    # Verifikasi port sekarang tersedia
    sleep 2
    NEW_PORT_STATUS=$(lsof -i:$PORT_TO_CHECK -t 2>/dev/null)
    if [ -z "$NEW_PORT_STATUS" ]; then
      echo "✅ Berhasil membebaskan port $PORT_TO_CHECK"
    else
      echo "❌ Gagal membebaskan port $PORT_TO_CHECK"
      exit 1
    fi
  else
    echo "Gunakan parameter --kill untuk menghentikan proses ini"
    echo "Contoh: ./check-ports.sh --kill --port $PORT_TO_CHECK"
  fi
fi

# Periksa port umum lainnya
if [ "$PORT_TO_CHECK" != "3000" ]; then
  echo -e "\nPort 3000:"
  lsof -i :3000 || echo "Port 3000 tersedia"
fi

if [ "$PORT_TO_CHECK" != "3001" ]; then
  echo -e "\nPort 3001:"
  lsof -i :3001 || echo "Port 3001 tersedia"
fi

if [ "$PORT_TO_CHECK" != "8002" ]; then
  echo -e "\nPort 8002 (API):"
  lsof -i :8002 || echo "Port 8002 tersedia"
fi

if [ "$PORT_TO_CHECK" != "8086" ]; then
  echo -e "\nPort 8086 (InfluxDB):"
  lsof -i :8086 || echo "Port 8086 tersedia"
fi

echo -e "\nJika ingin menghentikan proses yang menggunakan port tertentu,"
echo "gunakan: ./check-ports.sh --kill --port NOMOR_PORT"
