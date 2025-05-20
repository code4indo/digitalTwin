#!/usr/bin/env python3
"""
Script to verify that data is being written to InfluxDB correctly.
"""

from influxdb_client import InfluxDBClient
import os
from pprint import pprint

# --- Konfigurasi InfluxDB ---
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "iot_project_alpha")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "sensor_data_primary")

def check_influxdb_data():
    """Checks if data is available in InfluxDB for both weather and sensor readings."""
    print(f"Connecting to InfluxDB at {INFLUXDB_URL} with org {INFLUXDB_ORG} and bucket {INFLUXDB_BUCKET}")
    
    try:
        with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
            query_api = client.query_api()
            
            # Check BMKG Weather data
            print("\n=== BMKG Weather Forecast Data ===")
            # First, get count of records
            weather_count_query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
              |> range(start: -24h)
              |> filter(fn: (r) => r._measurement == "bmkg_weather_forecast")
              |> filter(fn: (r) => r.kode_wilayah == "31.74.04.1003")
              |> count()
              |> yield(name: "count")
            '''
            
            weather_count_result = query_api.query(weather_count_query)
            if weather_count_result:
                print("Count of BMKG weather forecast data:")
                for table in weather_count_result:
                    for record in table.records:
                        print(f"  - {record.get_field()}: {record.get_value()}")
                
                # Now get actual data samples
                # Get available tags first to understand the structure
                tag_query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -24h)
                  |> filter(fn: (r) => r._measurement == "bmkg_weather_forecast")
                  |> filter(fn: (r) => r.kode_wilayah == "31.74.04.1003")
                  |> first()
                  |> yield(name: "first_record")
                '''
                
                tag_result = query_api.query(tag_query)
                tag_info = {}
                if tag_result:
                    for table in tag_result:
                        for record in table.records:
                            print("\nAvailable BMKG data tags:")
                            for key, value in record.values.items():
                                if key not in ["_time", "_value", "_field", "_measurement", "result", "table", "_start", "_stop"]:
                                    tag_info[key] = value
                                    print(f"  - {key}: {value}")
                
                # Query for actual data samples
                weather_sample_query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -24h)
                  |> filter(fn: (r) => r._measurement == "bmkg_weather_forecast")
                  |> filter(fn: (r) => r.kode_wilayah == "31.74.04.1003")
                  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                  |> limit(n: 3)
                '''
                
                weather_sample_result = query_api.query(weather_sample_query)
                if weather_sample_result:
                    print("\nBMKG weather forecast data samples:")
                    for table in weather_sample_result:
                        for record in table.records:
                            # Build location string from available tags or fields
                            location = []
                            for loc_key in ["desa", "kecamatan", "kotkab", "provinsi"]:
                                # Check in both tags and fields
                                value = record.values.get(loc_key) or record.values.get(f"loc_{loc_key}")
                                if value and value != "N/A" and value != "":
                                    location.append(value)
                            
                            # Get weather description from tags or fields
                            weather_desc = record.values.get("weather_desc") or record.values.get("desc_weather_desc") or "N/A"
                            
                            print("\n  Record:")
                            print(f"    Time: {record.get_time()}")
                            print(f"    Location: {', '.join(location) if location else 'N/A'}")
                            print(f"    Coordinates: {record.values.get('latitude', 'N/A')}, {record.values.get('longitude', 'N/A')}")
                            print(f"    Weather: {weather_desc}")
                            print(f"    Temperature: {record.values.get('temperature', 'N/A')}°C")
                            print(f"    Humidity: {record.values.get('humidity', 'N/A')}%")
                            print(f"    Wind: {record.values.get('wind_speed', 'N/A')} km/h, {record.values.get('wind_direction_degree', 'N/A')}°")
                            print(f"    Visibility: {record.values.get('visibility_km', 'N/A')} km")
                else:
                    print("No BMKG weather forecast data samples found.")
            else:
                print("No BMKG weather forecast data found.")
                
                # Try a broader query to see if any data exists
                broader_query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -24h)
                  |> filter(fn: (r) => r._measurement == "bmkg_weather_forecast")
                  |> group(columns: ["kode_wilayah"])
                  |> count()
                  |> limit(n: 5)
                '''
                
                broader_result = query_api.query(broader_query)
                if broader_result:
                    print("Found some BMKG data with different kode_wilayah:")
                    for table in broader_result:
                        for record in table.records:
                            print(f"  - kode_wilayah: {record.values.get('kode_wilayah', 'N/A')}")
                else:
                    print("No BMKG data found at all in the database.")
            
            # Check sensor readings
            print("\n=== Sensor Reading Data ===")
            # First, get counts
            sensor_count_query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
              |> range(start: -24h)
              |> filter(fn: (r) => r._measurement == "sensor_reading")
              |> count()
              |> yield(name: "count")
            '''
            
            sensor_count_result = query_api.query(sensor_count_query)
            if sensor_count_result:
                print("Count of sensor reading data:")
                for table in sensor_count_result:
                    for record in table.records:
                        print(f"  - {record.get_field()}: {record.get_value()}")
                
                # Now get actual data samples
                sensor_sample_query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -24h)
                  |> filter(fn: (r) => r._measurement == "sensor_reading")
                  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                  |> sort(columns: ["_time"], desc: true)
                  |> limit(n: 10)
                '''
                
                sensor_sample_result = query_api.query(sensor_sample_query)
                if sensor_sample_result:
                    print("\nSensor reading data samples:")
                    for table in sensor_sample_result:
                        for record in table.records:
                            print("\n  Record:")
                            print(f"    Time: {record.get_time()}")
                            # Print all available fields and their values
                            for key, value in record.values.items():
                                if key != "_time" and key != "_measurement":
                                    print(f"    {key}: {value}")
            else:
                print("No sensor reading data found.")
                
    except Exception as e:
        print(f"Error checking InfluxDB data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_influxdb_data()
