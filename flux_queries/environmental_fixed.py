"""
Environmental Flux Queries
Berisi kueri untuk statistik lingkungan (suhu dan kelembaban) dari perangkat sensor
"""


def get_environmental_stats_query(bucket, range_filter_str, location_filter=""):
    """
    Menghasilkan kueri Flux untuk statistik lingkungan (suhu dan kelembaban)
    
    Args:
        bucket (str): Nama bucket InfluxDB
        range_filter_str (str): String filter rentang waktu Flux
        location_filter (str, optional): Filter lokasi. Default ke string kosong.
        
    Returns:
        str: Query Flux lengkap
    """
    return f'''
        temperature = from(bucket: "{bucket}")
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
              _measurement: "temperature",
              avg: if r.count > 0.0 then r.avg / r.count else 0.0,
              min: if r.count > 0.0 then r.min else 0.0,
              max: if r.count > 0.0 then r.max else 0.0,
              sample_count: r.count
          }}))
        
        humidity = from(bucket: "{bucket}")
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
              _measurement: "humidity",
              avg: if r.count > 0.0 then r.avg / r.count else 0.0,
              min: if r.count > 0.0 then r.min else 0.0,
              max: if r.count > 0.0 then r.max else 0.0,
              sample_count: r.count
          }}))
        
        union(tables: [temperature, humidity])
    '''
