"""
Humidity-related Flux Queries
Berisi kueri untuk statistik kelembaban dari perangkat sensor
"""


def get_humidity_stats_query(bucket, range_filter_str, location_filter=""):
    """
    Menghasilkan kueri Flux untuk statistik kelembaban
    
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
          |> filter(fn: (r) => r._measurement == "sensor_reading" and r._field == "humidity"{location_filter})
          |> group(columns: ["location", "device_id"])
          |> mean()
          |> group()
          |> map(fn: (r) => ({{
              _measurement: "humidity",
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
              avg_humidity: if r.count > 0.0 then r.avg / r.count else nil,
              min_humidity: if r.count > 0.0 then r.min else nil,
              max_humidity: if r.count > 0.0 then r.max else nil,
              sample_count: r.count
          }}))
    '''


def get_average_humidity_last_hour_query(bucket):
    """
    Menghasilkan kueri Flux untuk mendapatkan kelembaban rata-rata seluruh perangkat dalam 1 jam terakhir
    
    Args:
        bucket (str): Nama bucket InfluxDB
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
    from(bucket: "{bucket}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
      |> filter(fn: (r) => r["_field"] == "humidity")
      |> group(columns: ["location", "device_id"])
      |> mean()
      |> group()
      |> mean(column: "_value")
    '''


def get_min_humidity_last_hour_query(bucket):
    """
    Menghasilkan kueri Flux untuk mendapatkan kelembaban minimum dari seluruh perangkat dalam 1 jam terakhir
    
    Args:
        bucket (str): Nama bucket InfluxDB
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
    from(bucket: "{bucket}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
      |> filter(fn: (r) => r["_field"] == "humidity")
      |> group()
      |> min(column: "_value")
    '''


def get_max_humidity_last_hour_query(bucket):
    """
    Menghasilkan kueri Flux untuk mendapatkan kelembaban maksimum dari seluruh perangkat dalam 1 jam terakhir
    
    Args:
        bucket (str): Nama bucket InfluxDB
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
    from(bucket: "{bucket}")
      |> range(start: -1h)
      |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
      |> filter(fn: (r) => r["_field"] == "humidity")
      |> group()
      |> max(column: "_value")
    '''
