#!/usr/bin/env python3
"""
Script untuk mengumpulkan data training dari InfluxDB
dan mempersiapkannya untuk model machine learning
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime
import pandas as pd

# Add the project root to Python path
sys.path.append('/home/lambda_one/project/digitalTwin')

from services.ml_training_service import create_training_data_collector


async def collect_training_data(
    days_back: int = 30,
    location_filter: str = None,
    device_filter: str = None,
    include_external: bool = True,
    output_dir: str = "/app/data/training",
    output_filename: str = None
):
    """
    Mengumpulkan data training dari InfluxDB
    
    Args:
        days_back (int): Jumlah hari ke belakang
        location_filter (str): Filter lokasi
        device_filter (str): Filter device
        include_external (bool): Sertakan data cuaca eksternal
        output_dir (str): Direktori output
        output_filename (str): Nama file output
    """
    
    print("=" * 60)
    print("DIGITAL TWIN - PENGUMPULAN DATA TRAINING")
    print("=" * 60)
    print(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Periode: {days_back} hari terakhir")
    print(f"Lokasi filter: {location_filter or 'Semua lokasi'}")
    print(f"Device filter: {device_filter or 'Semua device'}")
    print(f"Sertakan data eksternal: {'Ya' if include_external else 'Tidak'}")
    print("-" * 60)
    
    try:
        # Create collector
        collector = create_training_data_collector()
        
        # Step 1: Collect indoor sensor data
        print("1. Mengumpulkan data sensor indoor...")
        indoor_data = await collector.collect_historical_data(
            days_back=days_back,
            location_filter=location_filter,
            device_filter=device_filter
        )
        
        if indoor_data.empty:
            print("❌ Tidak ada data sensor indoor ditemukan!")
            print("   Pastikan:")
            print("   - InfluxDB berjalan dan dapat diakses")
            print("   - Data sensor tersimpan di bucket 'sensor_data_primary'")
            print("   - Telegraf mengumpulkan data dari sensor")
            return False
        
        print(f"✓ Data indoor: {len(indoor_data)} records")
        print(f"  Rentang: {indoor_data['timestamp'].min()} - {indoor_data['timestamp'].max()}")
        
        # Step 2: Collect external weather data (optional)
        final_data = indoor_data
        if include_external:
            print("\n2. Mengumpulkan data cuaca eksternal...")
            external_data = await collector.get_external_weather_data(days_back=days_back)
            
            if external_data.empty:
                print("⚠️  Data cuaca eksternal tidak tersedia")
                print("   Melanjutkan dengan data indoor saja...")
            else:
                print(f"✓ Data eksternal: {len(external_data)} records")
                final_data = await collector.merge_with_external_data(indoor_data, external_data)
                print(f"✓ Data gabungan: {len(final_data)} records")
        
        # Step 3: Feature engineering
        print("\n3. Mempersiapkan features dan targets...")
        features, targets = await collector.prepare_training_features(final_data)
        
        print(f"✓ Features: {len(features)} samples, {len(features.columns)-1} features")
        print(f"✓ Targets: {len(targets)} samples, {len(targets.columns)-1} targets")
        
        # Step 4: Data quality report
        print("\n4. Laporan kualitas data:")
        print(f"  Total samples: {len(features)}")
        print(f"  Missing values: {features.isnull().sum().sum()}")
        print(f"  Temperature range: {final_data['temperature'].min():.1f}°C - {final_data['temperature'].max():.1f}°C")
        print(f"  Humidity range: {final_data['humidity'].min():.1f}% - {final_data['humidity'].max():.1f}%")
        
        if 'location' in final_data.columns:
            locations = final_data['location'].unique()
            print(f"  Locations: {list(locations)}")
        
        if 'device_id' in final_data.columns:
            devices = final_data['device_id'].unique()
            print(f"  Devices: {list(devices)}")
        
        # Step 5: Save data
        print("\n5. Menyimpan data training...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"training_data_{timestamp}.csv"
        
        filepath = os.path.join(output_dir, output_filename)
        
        success = await collector.save_training_data(features, targets, filepath)
        
        if success:
            print(f"✓ Data berhasil disimpan ke: {filepath}")
            
            # Save metadata
            metadata = {
                "generation_time": datetime.now().isoformat(),
                "days_back": days_back,
                "location_filter": location_filter,
                "device_filter": device_filter,
                "include_external": include_external,
                "total_samples": len(features),
                "feature_count": len(features.columns) - 1,
                "target_count": len(targets.columns) - 1,
                "date_range": {
                    "start": features['timestamp'].min().isoformat(),
                    "end": features['timestamp'].max().isoformat()
                },
                "data_quality": {
                    "missing_values": int(features.isnull().sum().sum()),
                    "completeness": round((1 - features.isnull().any(axis=1).sum() / len(features)) * 100, 2)
                }
            }
            
            metadata_file = filepath.replace('.csv', '_metadata.json')
            with open(metadata_file, 'w') as f:
                import json
                json.dump(metadata, f, indent=2)
            
            print(f"✓ Metadata disimpan ke: {metadata_file}")
            
        else:
            print("❌ Gagal menyimpan data training")
            return False
        
        print("\n" + "=" * 60)
        print("PENGUMPULAN DATA TRAINING BERHASIL!")
        print("=" * 60)
        print(f"File data: {filepath}")
        print(f"File metadata: {metadata_file}")
        print(f"Total samples: {len(features)}")
        print(f"Siap untuk training model machine learning!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Mengumpulkan data training untuk model ML Digital Twin')
    
    parser.add_argument('--days', type=int, default=30, 
                       help='Jumlah hari ke belakang untuk mengumpulkan data (default: 30)')
    parser.add_argument('--location', type=str, default=None, 
                       help='Filter berdasarkan lokasi (contoh: F2)')
    parser.add_argument('--device', type=str, default=None, 
                       help='Filter berdasarkan device ID (contoh: 2D3032)')
    parser.add_argument('--no-external', action='store_true', 
                       help='Jangan sertakan data cuaca eksternal')
    parser.add_argument('--output-dir', type=str, default='/tmp/training_data', 
                       help='Direktori output (default: /tmp/training_data)')
    parser.add_argument('--output-file', type=str, default=None, 
                       help='Nama file output (default: auto-generate)')
    
    args = parser.parse_args()
    
    # Run the collection
    success = asyncio.run(collect_training_data(
        days_back=args.days,
        location_filter=args.location,
        device_filter=args.device,
        include_external=not args.no_external,
        output_dir=args.output_dir,
        output_filename=args.output_file
    ))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
