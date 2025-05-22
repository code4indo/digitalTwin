"""
Data Queries
Berisi kueri untuk mengambil berbagai jenis data dari InfluxDB
"""


def get_sensor_data_query(bucket, range_filter_str, filter_expression, aggregation_str="", limit=100):
    """
    Menghasilkan kueri Flux untuk mengambil data sensor dengan opsi agregasi
    
    Args:
        bucket (str): Nama bucket InfluxDB
        range_filter_str (str): String filter rentang waktu Flux
        filter_expression (str): Ekspresi filter untuk memfilter data
        aggregation_str (str, optional): String agregasi. Default ke string kosong.
        limit (int, optional): Batas jumlah data yang dikembalikan. Default ke 100.
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
        from(bucket: "{bucket}")
          |> range({range_filter_str})
          |> filter(fn: (r) => {filter_expression})
          {aggregation_str} 
          |> pivot(rowKey:["_time", "device_id", "location", "source_ip", "hex_id_from_data"], columnKey: ["_field"], valueColumn: "_value")
          |> limit(n: {limit}) 
    '''


def get_general_sensor_data_query(bucket, range_filter_str, filter_expression, aggregation_str="", limit=100):
    """
    Alias untuk get_sensor_data_query untuk kompatibilitas dengan service layer
    """
    return get_sensor_data_query(bucket, range_filter_str, filter_expression, aggregation_str, limit)


def get_unique_devices_query(bucket, lookback_period="-30d"):
    """
    Menghasilkan kueri Flux untuk mendapatkan daftar perangkat unik yang tercatat dalam periode tertentu
    
    Args:
        bucket (str): Nama bucket InfluxDB
        lookback_period (str, optional): Periode waktu ke belakang. Default ke "-30d" (30 hari ke belakang).
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
        from(bucket: "{bucket}")
          |> range(start: {lookback_period})
          |> filter(fn: (r) => r._measurement == "sensor_reading")
          |> distinct(column: "device_id")
          |> group()
          |> map(fn: (r) => ({{
              device_id: r.device_id,
              location: r.location
          }}))
    '''


def get_device_history_query(bucket, device_id, lookback_period="-7d", field="temperature"):
    """
    Menghasilkan kueri Flux untuk mendapatkan riwayat data untuk satu perangkat tertentu
    
    Args:
        bucket (str): Nama bucket InfluxDB
        device_id (str): ID perangkat yang akan diambil datanya
        lookback_period (str, optional): Periode waktu ke belakang. Default ke "-7d" (7 hari ke belakang).
        field (str, optional): Kolom data yang akan diambil. Default ke "temperature".
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
        from(bucket: "{bucket}")
          |> range(start: {lookback_period})
          |> filter(fn: (r) => r._measurement == "sensor_reading" and r.device_id == "{device_id}" and r._field == "{field}")
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
    '''
