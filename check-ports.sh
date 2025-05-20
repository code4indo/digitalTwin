#!/bin/bash

echo "Memeriksa port yang sedang digunakan..."

# Periksa port 3000
echo "Port 3000:"
lsof -i :3000 || echo "Port 3000 tersedia"

# Periksa port 3001
echo "Port 3001:"
lsof -i :3001 || echo "Port 3001 tersedia"

# Periksa port 3003
echo "Port 3003:" 
lsof -i :3003 || echo "Port 3003 tersedia"

echo "Jika ingin menghentikan proses yang menggunakan port tertentu,"
echo "gunakan: kill -9 PID (ganti PID dengan Process ID yang ditampilkan)"
