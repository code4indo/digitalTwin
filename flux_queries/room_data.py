"""
Flux queries untuk mengambil data suhu dan kelembapan per ruangan.
"""

def get_room_environmental_data(room_id, start_time="-1h", end_time="now()"):
    """
    Mengambil data suhu dan kelembapan untuk ruangan tertentu.
    
    Args:
        room_id (str): ID ruangan (contoh: F2, G3, dsb)
        start_time (str): Waktu mulai dalam format Flux duration (contoh: -1h, -24h, -7d)
        end_time (str): Waktu akhir dalam format Flux duration (contoh: now())
        
    Returns:
        str: Query Flux untuk mengambil data lingkungan ruangan
    """
    query = f'''
    import "array"
    
    // Query untuk suhu
    temperature = from(bucket: "sensor_data_primary")
        |> range(start: {start_time}, stop: {end_time})
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "temperature")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> last()
        |> keep(columns: ["_time", "_value", "location"])
        |> rename(columns: {{"_value": "temperature"}})
    
    // Query untuk kelembapan
    humidity = from(bucket: "sensor_data_primary")
        |> range(start: {start_time}, stop: {end_time})
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "humidity")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> last()
        |> keep(columns: ["_time", "_value", "location"])
        |> rename(columns: {{"_value": "humidity"}})
    
    // Query untuk data harian
    daily_avg_temp = from(bucket: "sensor_data_primary")
        |> range(start: -24h, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "temperature")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> mean()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "daily_avg_temperature"}})
    
    daily_avg_humidity = from(bucket: "sensor_data_primary")
        |> range(start: -24h, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "humidity")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> mean()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "daily_avg_humidity"}})
    
    // Query untuk CO2 dan light jika tersedia
    co2_data = from(bucket: "sensor_data_primary")
        |> range(start: {start_time}, stop: {end_time})
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "co2")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> last()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "co2"}})
    
    light_data = from(bucket: "sensor_data_primary")
        |> range(start: {start_time}, stop: {end_time})
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "light")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> last()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "light"}})
    
    // Hitung persentase waktu dalam rentang optimal (misalnya suhu 18-24°C dan kelembapan 40-60%)
    optimal_temp_time = from(bucket: "sensor_data_primary")
        |> range(start: -24h, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "temperature")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> filter(fn: (r) => r["_value"] >= 18.0 and r["_value"] <= 24.0)
        |> count()
        |> keep(columns: ["_value"])
    
    total_temp_measurements = from(bucket: "sensor_data_primary")
        |> range(start: -24h, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "temperature")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> count()
        |> keep(columns: ["_value"])
    
    optimal_humidity_time = from(bucket: "sensor_data_primary")
        |> range(start: -24h, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "humidity")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> filter(fn: (r) => r["_value"] >= 40.0 and r["_value"] <= 60.0)
        |> count()
        |> keep(columns: ["_value"])
    
    total_humidity_measurements = from(bucket: "sensor_data_primary")
        |> range(start: -24h, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "humidity")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> count()
        |> keep(columns: ["_value"])
    
    // Gabungkan semua data
    temperature
        |> join(tables: {{humidity: humidity}}, on: ["location"])
        |> yield(name: "current_conditions")
    
    daily_avg_temp
        |> join(tables: {{humidity: daily_avg_humidity}}, on: [])
        |> yield(name: "daily_averages")
    
    co2_data
        |> join(tables: {{light: light_data}}, on: [])
        |> yield(name: "environmental_factors")
    
    optimal_temp_time
        |> join(tables: {{total: total_temp_measurements}}, on: [])
        |> map(fn: (r) => ({{
            optimal_temp_percentage: float(v: if exists r._value_optimal_temp_time and exists r._value_total_temp_measurements and r._value_total_temp_measurements > 0 
                then (r._value_optimal_temp_time / r._value_total_temp_measurements) * 100.0 
                else 0.0
        }}))
        |> yield(name: "optimal_temp_percentage")
    
    optimal_humidity_time
        |> join(tables: {{total: total_humidity_measurements}}, on: [])
        |> map(fn: (r) => ({{
            optimal_humidity_percentage: float(v: if exists r._value_optimal_humidity_time and exists r._value_total_humidity_measurements and r._value_total_humidity_measurements > 0 
                then (r._value_optimal_humidity_time / r._value_total_humidity_measurements) * 100.0 
                else 0.0
        }}))
        |> yield(name: "optimal_humidity_percentage")
    '''
    
    return query


def get_room_device_status(room_id, start_time="-10m", end_time="now()"):
    """
    Mengambil status perangkat untuk ruangan tertentu.
    
    Args:
        room_id (str): ID ruangan (contoh: F2, G3, dsb)
        start_time (str): Waktu mulai dalam format Flux duration (contoh: -1h, -24h, -7d)
        end_time (str): Waktu akhir dalam format Flux duration (contoh: now())
        
    Returns:
        str: Query Flux untuk mengambil status perangkat
    """
    query = f'''
    // Query untuk status AC
    ac_status = from(bucket: "sensor_data_primary")
        |> range(start: {start_time}, stop: {end_time})
        |> filter(fn: (r) => r["_measurement"] == "device_status" and r["device_type"] == "ac")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> last()
        |> keep(columns: ["_value", "device_id", "set_point"])
        |> rename(columns: {{"_value": "status"}})
    
    // Query untuk status Dehumidifier
    dehumidifier_status = from(bucket: "sensor_data_primary")
        |> range(start: {start_time}, stop: {end_time})
        |> filter(fn: (r) => r["_measurement"] == "device_status" and r["device_type"] == "dehumidifier")
        |> filter(fn: (r) => r["location"] == "{room_id}")
        |> last()
        |> keep(columns: ["_value", "device_id", "set_point"])
        |> rename(columns: {{"_value": "status"}})
    
    // Yield semua hasil
    ac_status
        |> yield(name: "ac_status")
    
    dehumidifier_status
        |> yield(name: "dehumidifier_status")
    '''
    
    return query
