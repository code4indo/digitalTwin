#!/usr/bin/env python3
"""
Digital Twin System - Main Runner
Menjalankan semua komponen sistem Digital Twin
"""

import os
import subprocess
import threading
import time
import signal
import sys

# Daftar proses yang akan dijalankan
processes = []

def run_command(command, name):
    """Menjalankan perintah shell sebagai subprocess"""
    print(f"Starting {name}...")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    processes.append((process, name))
    
    # Log output
    while True:
        output = process.stdout.readline()
        if output:
            print(f"[{name}] {output.strip()}")
        
        # Check if process has terminated
        if process.poll() is not None:
            break
    
    # Read remaining output
    for output in process.stdout.readlines():
        if output:
            print(f"[{name}] {output.strip()}")
    
    print(f"{name} terminated with exit code {process.returncode}")

def start_data_acquisition():
    """Memulai proses pengumpulan data dari perangkat"""
    command = "python3 acquire_device_data.py"
    threading.Thread(target=run_command, args=(command, "Data Acquisition"), daemon=True).start()

def start_bmkg_collector():
    """Memulai proses pengumpulan data BMKG"""
    command = "python3 bmkg_data_collector.py"
    threading.Thread(target=run_command, args=(command, "BMKG Collector"), daemon=True).start()

def start_api_server():
    """Memulai API server"""
    # Menggunakan python3 api.py yang sekarang dikonfigurasi untuk mendengarkan di 0.0.0.0:8002
    command = "python3 api.py"
    threading.Thread(target=run_command, args=(command, "API Server"), daemon=True).start()

def start_web_interface():
    """Memulai web interface digital twin"""
    command = "python3 web_server.py"
    threading.Thread(target=run_command, args=(command, "Web Interface"), daemon=True).start()

def handle_exit(signum, frame):
    """Handler untuk sinyal termination untuk shutdown yang bersih"""
    print("\nShutting down Digital Twin system...")
    
    # Terminasi semua proses
    for process, name in processes:
        print(f"Terminating {name}...")
        process.terminate()
    
    # Berikan waktu untuk shutdown yang bersih
    time.sleep(2)
    
    # Force kill jika masih ada yang berjalan
    for process, name in processes:
        if process.poll() is None:
            print(f"Force killing {name}...")
            process.kill()
    
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    print("Starting Digital Twin System...")
    
    # Start all components
    start_data_acquisition()
    time.sleep(2)  # Berikan waktu untuk proses pertama dimulai
    
    start_bmkg_collector()
    time.sleep(2)
    
    start_api_server()
    time.sleep(2)
    
    start_web_interface()
    
    print("All components started. Press Ctrl+C to stop the system.")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
