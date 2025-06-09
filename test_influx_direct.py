"""
Script untuk test query InfluxDB secara langsung
"""
import os
from influxdb_client import InfluxDBClient

# Konfigurasi
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "iot_project_alpha")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET_PRIMARY", "sensor_data_primary")

def test_basic_query():
    """Test query dasar untuk melihat apakah ada data"""
    try:
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        query_api = client.query_api()
        
        # Query sederhana untuk melihat data terakhir
        simple_query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -1h)
            |> filter(fn: (r) => r["_measurement"] == "sensor_data")
            |> filter(fn: (r) => r["_field"] == "temperature")
            |> last()
        '''
        
        print("Testing basic query...")
        print(f"Query: {simple_query}")
        
        result = query_api.query(query=simple_query)
        
        if result:
            print(f"Found {len(result)} tables")
            for table in result:
                print(f"Table: {table.name}, Records: {len(table.records)}")
                for record in table.records[:3]:  # Print first 3 records
                    print(f"  Time: {record.get_time()}, Value: {record.get_value()}, Location: {record.values.get('location', 'N/A')}")
        else:
            print("No data found")
            
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

def test_hourly_aggregation():
    """Test aggregasi per jam"""
    try:
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        query_api = client.query_api()
        
        # Query agregasi per jam
        hourly_query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -24h)
            |> filter(fn: (r) => r["_measurement"] == "sensor_data")
            |> filter(fn: (r) => r["_field"] == "temperature")
            |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
            |> sort(columns: ["_time"])
        '''
        
        print("\nTesting hourly aggregation...")
        print(f"Query: {hourly_query}")
        
        result = query_api.query(query=hourly_query)
        
        if result:
            print(f"Found {len(result)} tables")
            total_records = 0
            for table in result:
                total_records += len(table.records)
                print(f"Table: {table.name}, Records: {len(table.records)}")
                for record in table.records[:3]:  # Print first 3 records
                    print(f"  Time: {record.get_time()}, Value: {record.get_value()}, Location: {record.values.get('location', 'N/A')}")
            print(f"Total records: {total_records}")
        else:
            print("No aggregated data found")
            
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_basic_query()
    test_hourly_aggregation()
