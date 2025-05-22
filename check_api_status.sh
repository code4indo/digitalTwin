#!/bin/bash
# Script untuk memeriksa dan memastikan API container berjalan

echo "==== Memeriksa status container API ===="
API_CONTAINER="api_service"
CONTAINER_STATUS=$(docker ps -f "name=$API_CONTAINER" --format "{{.Status}}" 2>/dev/null)

if [ -z "$CONTAINER_STATUS" ]; then
    echo "Container $API_CONTAINER tidak ditemukan dalam status 'running'."
    echo "Mencoba menjalankan docker-compose up untuk container API..."
    
    cd "$(dirname "$0")"  # Pindah ke direktori script
    docker-compose up -d api
    
    # Tunggu beberapa saat untuk container mulai
    echo "Menunggu container API mulai..."
    sleep 10
    
    # Periksa status lagi
    CONTAINER_STATUS=$(docker ps -f "name=$API_CONTAINER" --format "{{.Status}}" 2>/dev/null)
    if [ -z "$CONTAINER_STATUS" ]; then
        echo "GAGAL: Container $API_CONTAINER masih tidak berjalan."
        echo "Periksa log dengan: docker logs $API_CONTAINER"
        exit 1
    else
        echo "SUKSES: Container $API_CONTAINER sekarang berjalan."
        echo "Status: $CONTAINER_STATUS"
    fi
else
    echo "Container $API_CONTAINER sudah berjalan."
    echo "Status: $CONTAINER_STATUS"
fi

echo -e "\n==== Memeriksa healthcheck API ===="
API_URL="http://localhost:8002/system/health/"
API_KEY="development_key_for_testing"  # Dari docker-compose.yml

echo "Mengirim request ke: $API_URL"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" $API_URL)

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "API healthcheck OK (HTTP 200)"
    
    # Menampilkan respon lengkap untuk informasi
    echo -e "\nDetail healthcheck response:"
    curl -s -H "X-API-Key: $API_KEY" $API_URL | python3 -m json.tool
else
    echo "API healthcheck GAGAL (HTTP $HTTP_STATUS)"
    
    # Coba dapatkan pesan error
    ERROR_MSG=$(curl -s -H "X-API-Key: $API_KEY" $API_URL)
    echo "Error response: $ERROR_MSG"
    
    # Lihat log untuk debug
    echo -e "\nContainer logs terakhir:"
    docker logs --tail 20 $API_CONTAINER
fi

echo -e "\n==== Memeriksa endpoint statistik lingkungan ===="
ENDPOINT="http://localhost:8002/stats/environmental/"

echo "Mengirim request ke: $ENDPOINT"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" $ENDPOINT)

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "Endpoint statistik lingkungan OK (HTTP 200)"
    
    # Menampilkan respon lengkap
    echo -e "\nDetail response:"
    curl -s -H "X-API-Key: $API_KEY" $ENDPOINT | python3 -m json.tool
    echo -e "\n✅ Endpoint statistik lingkungan berfungsi dengan baik!"
else
    echo "Endpoint statistik lingkungan GAGAL (HTTP $HTTP_STATUS)"
    
    # Coba dapatkan pesan error
    ERROR_MSG=$(curl -s -H "X-API-Key: $API_KEY" $ENDPOINT)
    echo "Error response: $ERROR_MSG"
    
    echo -e "\n❌ Endpoint statistik lingkungan tidak tersedia atau mengalami error."
fi

exit 0
