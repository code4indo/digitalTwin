#!/bin/bash

# Script untuk mengatur Gemini API Key untuk AI Insights

echo "=== Pengaturan Gemini API Key untuk Digital Twin ==="
echo ""

if [ -f ".env" ]; then
    echo "File .env ditemukan"
else
    echo "Membuat file .env..."
    cp .env.example .env 2>/dev/null || touch .env
fi

echo ""
echo "Untuk mendapatkan Gemini API Key:"
echo "1. Kunjungi: https://makersuite.google.com/app/apikey"
echo "2. Login dengan akun Google"
echo "3. Buat API key baru"
echo "4. Copy API key yang dihasilkan"
echo ""

read -p "Masukkan Gemini API Key Anda (atau tekan Enter untuk skip): " api_key

if [ ! -z "$api_key" ]; then
    # Update atau tambah GEMINI_API_KEY di .env
    if grep -q "GEMINI_API_KEY=" .env; then
        # Update existing
        sed -i "s/^.*GEMINI_API_KEY=.*/GEMINI_API_KEY=$api_key/" .env
        echo "✅ Gemini API Key berhasil diupdate di .env"
    else
        # Add new
        echo "" >> .env
        echo "GEMINI_API_KEY=$api_key" >> .env
        echo "✅ Gemini API Key berhasil ditambahkan di .env"
    fi
    
    echo ""
    echo "Restarting containers untuk mengaplikasikan perubahan..."
    docker-compose restart api
    
    echo ""
    echo "✅ Setup selesai! AI Insights sekarang menggunakan Gemini AI."
    echo ""
    echo "Test endpoint insights:"
    echo "curl -X GET \"http://localhost:8002/insights/climate-analysis?parameter=temperature&period=day&location=all\" -H \"x-api-key: development_key_for_testing\""
    
else
    echo ""
    echo "⚠️  API key tidak diatur. Sistem akan tetap menggunakan rule-based fallback."
    echo ""
    echo "Untuk mengatur API key nanti, edit file .env dan uncomment/set:"
    echo "GEMINI_API_KEY=your_actual_api_key"
    echo ""
    echo "Kemudian restart containers dengan: docker-compose restart api"
fi

echo ""
echo "=== Setup selesai ==="
