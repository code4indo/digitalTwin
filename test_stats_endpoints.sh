#!/bin/bash
# Script untuk menguji endpoint statistik lingkungan baru

API_URL="http://localhost:8002"
API_KEY="development_key_for_testing"  # Dari docker-compose.yml

# Fungsi untuk menguji endpoint dan menampilkan hasil
test_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -e "\n===== Menguji $description ====="
    echo "URL: $API_URL$endpoint"
    
    # Panggil endpoint dengan curl
    HTTP_STATUS=$(curl -s -o /tmp/api_response.json -w "%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL$endpoint")
    
    if [ "$HTTP_STATUS" -eq 200 ]; then
        echo "✅ Status: SUKSES (HTTP $HTTP_STATUS)"
        echo "Respon:"
        cat /tmp/api_response.json | python3 -m json.tool
    else
        echo "❌ Status: GAGAL (HTTP $HTTP_STATUS)"
        echo "Error response:"
        cat /tmp/api_response.json
    fi
}

# Header utama
echo "==============================================================="
echo "PENGUJIAN ENDPOINT API STATISTIK LINGKUNGAN"
echo "==============================================================="
echo "Waktu pengujian: $(date '+%Y-%m-%d %H:%M:%S')"
echo "API URL: $API_URL"
echo "==============================================================="

# Uji endpoint suhu
test_endpoint "/stats/temperature/" "Endpoint Statistik Suhu"

# Uji endpoint kelembapan
test_endpoint "/stats/humidity/" "Endpoint Statistik Kelembapan"

# Uji endpoint gabungan
test_endpoint "/stats/environmental/" "Endpoint Statistik Lingkungan (Gabungan)"

# Uji dengan filter lokasi - ganti dengan lokasi valid di sistem Anda jika perlu
test_endpoint "/stats/environmental/?locations=R.Arsip-1" "Endpoint dengan Filter Lokasi"

# Uji dengan rentang waktu kustom (1 jam terakhir)
start_time=$(date -u -d "1 hour ago" '+%Y-%m-%dT%H:%M:%SZ')
test_endpoint "/stats/environmental/?start_time=$start_time" "Endpoint dengan Filter Waktu (1 jam terakhir)"

echo -e "\n==============================================================="
echo "PENGUJIAN SELESAI"
echo "==============================================================="

exit 0
