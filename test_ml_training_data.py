#!/usr/bin/env python3
"""
Test script untuk menguji pengumpulan data training dari InfluxDB
"""

import asyncio
import json
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append('/home/lambda_one/project/digitalTwin')

from services.ml_training_service import create_training_data_collector


async def test_training_data_collection():
    """
    Test function untuk mengumpulkan data training
    """
    print("=" * 50)
    print("TEST: Pengumpulan Data Training dari InfluxDB")
    print("=" * 50)
    
    try:
        # Create collector
        collector = create_training_data_collector()
        print("✓ TrainingDataCollector berhasil dibuat")
        
        # Test 1: Get data statistics
        print("\n1. Mengumpulkan statistik data...")
        data = await collector.collect_historical_data(days_back=7)
        
        if data.empty:
            print("⚠️  Tidak ada data historis ditemukan dalam 7 hari terakhir")
            print("   Coba dengan rentang waktu yang lebih panjang...")
            
            # Try with longer period
            data = await collector.collect_historical_data(days_back=30)
            
            if data.empty:
                print("❌ Tidak ada data historis ditemukan dalam 30 hari terakhir")
                print("   Pastikan:")
                print("   - InfluxDB running dan dapat diakses")
                print("   - Data sensor sudah tersimpan di bucket 'sensor_data_primary'")
                print("   - Telegraf sudah mengumpulkan data")
                return False
        
        print(f"✓ Data historis ditemukan: {len(data)} records")
        print(f"  - Rentang waktu: {data['timestamp'].min()} sampai {data['timestamp'].max()}")
        
        if 'location' in data.columns:
            locations = data['location'].unique()
            print(f"  - Lokasi: {list(locations)}")
        
        if 'device_id' in data.columns:
            devices = data['device_id'].unique()
            print(f"  - Device ID: {list(devices)}")
        
        # Test 2: Data quality check
        print("\n2. Mengecek kualitas data...")
        print(f"  - Total records: {len(data)}")
        print(f"  - Missing temperature: {data['temperature'].isna().sum()}")
        print(f"  - Missing humidity: {data['humidity'].isna().sum()}")
        print(f"  - Temperature range: {data['temperature'].min():.1f}°C - {data['temperature'].max():.1f}°C")
        print(f"  - Humidity range: {data['humidity'].min():.1f}% - {data['humidity'].max():.1f}%")
        
        # Test 3: Feature engineering
        print("\n3. Test feature engineering...")
        features, targets = await collector.prepare_training_features(data)
        
        print(f"✓ Features berhasil disiapkan: {len(features)} samples")
        print(f"  - Feature columns: {len(features.columns) - 1}")  # minus timestamp
        print(f"  - Target columns: {len(targets.columns) - 1}")    # minus timestamp
        
        print("\n  Feature columns:")
        for col in features.columns:
            if col != 'timestamp':
                print(f"    - {col}")
        
        # Test 4: External weather data
        print("\n4. Test data cuaca eksternal...")
        external_data = await collector.get_external_weather_data(days_back=7)
        
        if external_data.empty:
            print("⚠️  Tidak ada data cuaca eksternal ditemukan")
            print("   Pastikan BMKG data collector sudah berjalan")
        else:
            print(f"✓ Data cuaca eksternal ditemukan: {len(external_data)} records")
            
            # Test merging
            merged_data = await collector.merge_with_external_data(data, external_data)
            print(f"✓ Data berhasil digabungkan: {len(merged_data)} records")
        
        # Test 5: Save sample data
        print("\n5. Test penyimpanan data...")
        sample_features = features.head(100)
        sample_targets = targets.head(100)
        
        test_filepath = "/tmp/test_training_data.csv"
        success = await collector.save_training_data(
            sample_features, 
            sample_targets, 
            test_filepath
        )
        
        if success:
            print(f"✓ Sample data berhasil disimpan ke {test_filepath}")
        else:
            print("❌ Gagal menyimpan sample data")
        
        print("\n" + "=" * 50)
        print("SUMMARY: Test Berhasil!")
        print("=" * 50)
        print(f"✓ Data training tersedia: {len(data)} records")
        print(f"✓ Features tersedia: {len(features.columns) - 1} features")
        print(f"✓ Ready untuk training model ML")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Pastikan InfluxDB running pada port 8086")
        print("2. Pastikan bucket 'sensor_data_primary' ada dan berisi data")
        print("3. Pastikan token InfluxDB valid")
        print("4. Pastikan Telegraf sudah mengumpulkan data sensor")
        return False


async def test_api_endpoints():
    """
    Test API endpoints untuk ML training data
    """
    print("\n" + "=" * 50)
    print("TEST: API Endpoints untuk ML Training")
    print("=" * 50)
    
    import requests
    
    # Test endpoints
    base_url = "http://localhost:8002"
    api_key = "development_key_for_testing"
    headers = {"X-API-Key": api_key}
    
    endpoints = [
        ("/ml/training-data/stats?days_back=7", "Training Data Statistics"),
        ("/ml/data/sample?limit=10", "Sample Data"),
        ("/ml/training-data/collect?days_back=7&save_to_file=false", "Collect Training Data")
    ]
    
    for endpoint, description in endpoints:
        try:
            print(f"\nTesting: {description}")
            print(f"URL: {base_url}{endpoint}")
            
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {description}: OK")
                if 'stats' in data:
                    print(f"  Total records: {data['stats'].get('total_records', 'N/A')}")
                elif 'data_info' in data:
                    print(f"  Total samples: {data['data_info'].get('total_samples', 'N/A')}")
                elif 'sample_size' in data:
                    print(f"  Sample size: {data['sample_size']}")
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: Connection error - {e}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")


if __name__ == "__main__":
    print("Digital Twin ML Training Data Test")
    print("Tanggal:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Test 1: Direct service test
    success = asyncio.run(test_training_data_collection())
    
    if success:
        # Test 2: API endpoints test
        print("\nMemulai test API endpoints...")
        print("Pastikan API server berjalan pada port 8002...")
        asyncio.run(test_api_endpoints())
    
    print("\nTest selesai!")
