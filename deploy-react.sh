#!/bin/bash

# Script untuk membangun dan men-deploy aplikasi React ke folder web
# Penggunaan: ./deploy-react.sh

echo "Membangun aplikasi React untuk Digital Twin..."
cd "$(dirname "$0")/web-react"

# Pastikan semua dependensi diinstal
echo "Menginstal dependensi..."
npm install

# Build aplikasi React
echo "Membangun aplikasi..."
npm run build

# Siapkan direktori web baru (cadangkan yang lama jika ada)
if [ -d "../web-backup" ]; then
  echo "Menghapus backup sebelumnya..."
  rm -rf "../web-backup"
fi

if [ -d "../web" ]; then
  echo "Mencadangkan web lama ke web-backup..."
  mv "../web" "../web-backup"
fi

# Pindahkan hasil build ke folder web
echo "Memindahkan hasil build ke folder web..."
mv "dist" "../web"

# Salin file aset yang mungkin tidak dibangun oleh webpack
if [ -d "../web-backup/img" ] && [ ! -d "../web/img" ]; then
  echo "Menyalin folder img dari backup..."
  cp -r "../web-backup/img" "../web/"
fi

echo "Deployment selesai! Aplikasi React telah berhasil diterapkan."
