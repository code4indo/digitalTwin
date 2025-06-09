#!/usr/bin/env python3
"""
Script untuk membersihkan dan memverifikasi data BMKG di InfluxDB
"""

import os
from influxdb_client import InfluxDBClient
from datetime import datetime

# Konfigurasi InfluxDB
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v"
INFLUXDB_ORG = "iot_project_alpha"
INFLUXDB_BUCKET = "sensor_data_primary"

def clean_bmkg_data():
    """Bersihkan data BMKG yang bermasalah"""
    print("🧹 Cleaning BMKG data from InfluxDB...")
    
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    
    try:
        # Delete API
        delete_api = client.delete_api()
        
        # Delete all bmkg_weather_forecast measurements
        start = "1970-01-01T00:00:00Z"
        stop = "2025-12-31T23:59:59Z"
        
        delete_api.delete(
            start=start,
            stop=stop,
            predicate='_measurement="bmkg_weather_forecast"',
            bucket=INFLUXDB_BUCKET
        )
        
        print("✅ BMKG data cleaned successfully")
        
    except Exception as e:
        print(f"❌ Error cleaning data: {e}")
    finally:
        client.close()

def verify_bmkg_data():
    """Verifikasi data BMKG di InfluxDB"""
    print("\n🔍 Verifying BMKG data in InfluxDB...")
    
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    
    try:
        query_api = client.query_api()
        
        # Query untuk mengecek data BMKG
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -7d)
        |> filter(fn: (r) => r["_measurement"] == "bmkg_weather_forecast")
        |> count()
        '''
        
        tables = query_api.query(query)
        
        total_records = 0
        for table in tables:
            for record in table.records:
                total_records += record.get_value()
        
        print(f"📊 Total BMKG records in last 7 days: {total_records}")
        
        if total_records > 0:
            # Get latest record
            latest_query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -7d)
            |> filter(fn: (r) => r["_measurement"] == "bmkg_weather_forecast")
            |> last()
            '''
            
            latest_tables = query_api.query(latest_query)
            
            print("📋 Latest BMKG data:")
            for table in latest_tables:
                for record in table.records:
                    field = record.get_field()
                    value = record.get_value()
                    time = record.get_time()
                    print(f"   {field}: {value} (at {time})")
        else:
            print("❌ No BMKG data found")
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
    finally:
        client.close()

def test_bmkg_endpoint():
    """Test endpoint BMKG"""
    print("\n🌐 Testing BMKG endpoint...")
    
    import requests
    
    try:
        response = requests.get(
            "http://localhost:8002/external/bmkg/latest",
            headers={"X-API-Key": "development_key_for_testing"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ BMKG endpoint responding")
            print(f"📊 Data source: {data.get('data_source', 'unknown')}")
            print(f"🌡️  Temperature: {data.get('weather_data', {}).get('temperature', 'N/A')}°C")
            print(f"💧 Humidity: {data.get('weather_data', {}).get('humidity', 'N/A')}%")
            print(f"🕒 Last updated: {data.get('last_updated', 'N/A')}")
            
            if 'Fallback' in data.get('data_source', ''):
                print("⚠️  Currently using fallback data")
            elif 'error' in data:
                print(f"❌ Error in response: {data['error']}")
        else:
            print(f"❌ Endpoint error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 BMKG Data Cleanup and Verification")
    print("=" * 60)
    
    clean_bmkg_data()
    verify_bmkg_data()
    test_bmkg_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ BMKG cleanup and verification completed")
    print("=" * 60)
