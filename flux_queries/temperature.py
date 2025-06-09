"""
Temperature-related Flux Quer              identity: {"avg": 0.0, "min": 1000.0, "max": -1000.0, "count": 0.0},es
Berisi kueri untuk statistik suhu dari perangkat sensor
"""


def get_temperature_stats_query(bucket, range_filter_str, location_filter=""):
    """
    Menghasilkan kueri Flux untuk statistik suhu
    
    Args:
        bucket (str): Nama bucket InfluxDB
        range_filter_str (str): String filter rentang waktu Flux
        location_filter (str, optional): Filter lokasi. Default ke string kosong.
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
        from(bucket: "{bucket}")
          |> range({range_filter_str})
          |> filter(fn: (r) => r._measurement == "sensor_reading" and r._field == "temperature"{location_filter})
          |> group(columns: ["location", "device_id"])
          |> mean()
          |> group()
          |> map(fn: (r) => ({{
              _measurement: "temperature",
              avg: r._value,
              min: r._value,
              max: r._value,
              sample_count: 1.0
          }}))
          |> reduce(
              identity: {{"avg": 0.0, "min": +1000.0, "max": -1000.0, "count": 0.0}},
              fn: (r, accumulator) => ({{
                  avg: accumulator.avg + r.avg,
                  min: if r.min < accumulator.min then r.min else accumulator.min,
                  max: if r.max > accumulator.max then r.max else accumulator.max,
                  count: accumulator.count + r.sample_count
              }})
          )
          |> map(fn: (r) => ({{
              avg_temperature: if r.count > 0.0 then r.avg / r.count else 0.0,
              min_temperature: if r.count > 0.0 then r.min else 0.0,
              max_temperature: if r.count > 0.0 then r.max else 0.0,
              sample_count: r.count
          }}))
    '''


def get_average_temperature_last_hour_query(bucket):
    """
    Menghasilkan kueri Flux untuk mendapatkan suhu rata-rata seluruh perangkat dalam 1 jam terakhir
    
    Args:
        bucket (str): Nama bucket InfluxDB
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
    from(bucket: "{bucket}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
      |> filter(fn: (r) => r["_field"] == "temperature")
      |> group(columns: ["location", "device_id"])
      |> mean()
      |> group()
      |> mean(column: "_value")
    '''


def get_min_temperature_last_hour_query(bucket):
    """
    Menghasilkan kueri Flux untuk mendapatkan suhu minimum seluruh perangkat dalam 1 jam terakhir
    
    Args:
        bucket (str): Nama bucket InfluxDB
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
    from(bucket: "{bucket}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
      |> filter(fn: (r) => r["_field"] == "temperature")
      |> group()
      |> min(column: "_value")
    '''


def get_max_temperature_last_hour_query(bucket):
    """
    Menghasilkan kueri Flux untuk mendapatkan suhu maksimum seluruh perangkat dalam 1 jam terakhir
    
    Args:
        bucket (str): Nama bucket InfluxDB
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
    from(bucket: "{bucket}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
      |> filter(fn: (r) => r["_field"] == "temperature")
      |> group()
      |> max(column: "_value")
    '''


def get_temperature_stats_last_hour_query(bucket):
    """
    Menghasilkan kueri Flux untuk mendapatkan statistik suhu (min, avg, max) seluruh perangkat dalam 1 jam terakhir
    
    Args:
        bucket (str): Nama bucket InfluxDB
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
    from(bucket: "{bucket}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
      |> filter(fn: (r) => r["_field"] == "temperature")
      |> group()
      |> reduce(
          identity: {{"avg": 0.0, "min": 1000.0, "max": -1000.0, "count": 0.0}},
          fn: (r, accumulator) => ({{
              avg: accumulator.avg + r._value,
              min: if r._value < accumulator.min then r._value else accumulator.min,
              max: if r._value > accumulator.max then r._value else accumulator.max,
              count: accumulator.count + 1.0
          }})
      )
      |> map(fn: (r) => ({{
          avg_temperature: r.avg / r.count,
          min_temperature: r.min,
          max_temperature: r.max,
          sample_count: r.count
      }}))
    '''


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
