"""
Optimized Flux Queries untuk mengumpulkan data training ML
Queries ini dioptimasi untuk performa dan kelengkapan data
"""

def get_training_data_query(bucket: str, days_back: int = 30, location_filter: str = None, device_filter: str = None) -> str:
    """
    Query Flux untuk mengambil data training lengkap dengan semua field yang dibutuhkan
    
    Args:
        bucket (str): Nama bucket InfluxDB
        days_back (int): Jumlah hari ke belakang
        location_filter (str, optional): Filter lokasi spesifik
        device_filter (str, optional): Filter device spesifik
        
    Returns:
        str: Query Flux yang optimized
    """
    
    # Build filters
    additional_filters = ""
    if location_filter:
        additional_filters += f' and r.location == "{location_filter}"'
    if device_filter:
        additional_filters += f' and r.device_id == "{device_filter}"'
    
    query = f'''
    // Optimized training data query for Digital Twin ML
    import "math"
    import "interpolate"
    
    // Define time range
    start_time = -{days_back}d
    end_time = now()
    
    // Get sensor data with proper interpolation for missing values
    sensor_data = from(bucket: "{bucket}")
      |> range(start: start_time, stop: end_time)
      |> filter(fn: (r) => r._measurement == "sensor_reading"{additional_filters})
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
      |> aggregateWindow(every: 10m, fn: mean, createEmpty: true)
      |> interpolate.linear(every: 10m)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> keep(columns: ["_time", "temperature", "humidity", "location", "device_id"])
      |> filter(fn: (r) => exists r.temperature and exists r.humidity)
      |> sort(columns: ["_time"])
    
    // Add time-based features
    enhanced_data = sensor_data
      |> map(fn: (r) => ({{
          r with
          hour: int(v: date.hour(t: r._time)),
          day_of_week: int(v: date.weekDay(t: r._time)),
          month: int(v: date.month(t: r._time)),
          is_weekend: if int(v: date.weekDay(t: r._time)) >= 6 then 1 else 0
      }}))
    
    // Return the enhanced dataset
    enhanced_data
    '''
    
    return query


def get_external_weather_query(bucket: str, days_back: int = 30) -> str:
    """
    Query untuk data cuaca eksternal dari BMKG
    
    Args:
        bucket (str): Nama bucket InfluxDB
        days_back (int): Jumlah hari ke belakang
        
    Returns:
        str: Query Flux untuk data cuaca eksternal
    """
    
    query = f'''
    // External weather data from BMKG
    from(bucket: "{bucket}")
      |> range(start: -{days_back}d)
      |> filter(fn: (r) => r._measurement == "bmkg_weather")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity" or r._field == "weather_code")
      |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> keep(columns: ["_time", "temperature", "humidity", "weather_code"])
      |> rename(columns: {{temperature: "outdoor_temp", humidity: "outdoor_humidity"}})
      |> sort(columns: ["_time"])
    '''
    
    return query


def get_device_status_query(bucket: str, days_back: int = 30) -> str:
    """
    Query untuk status perangkat dan konektivitas
    
    Args:
        bucket (str): Nama bucket InfluxDB
        days_back (int): Jumlah hari ke belakang
        
    Returns:
        str: Query untuk status perangkat
    """
    
    query = f'''
    // Device status and connectivity data
    from(bucket: "{bucket}")
      |> range(start: -{days_back}d)
      |> filter(fn: (r) => r._measurement == "sensor_reading")
      |> group(columns: ["device_id", "location"])
      |> aggregateWindow(every: 1h, fn: count, createEmpty: true)
      |> map(fn: (r) => ({{
          _time: r._time,
          device_id: r.device_id,
          location: r.location,
          data_points_per_hour: r._value,
          connectivity_score: if r._value >= 5 then 1.0 else float(v: r._value) / 6.0
      }}))
      |> keep(columns: ["_time", "device_id", "location", "data_points_per_hour", "connectivity_score"])
      |> sort(columns: ["_time"])
    '''
    
    return query


def get_anomaly_detection_query(bucket: str, days_back: int = 30) -> str:
    """
    Query untuk deteksi anomali pada data sensor
    
    Args:
        bucket (str): Nama bucket InfluxDB
        days_back (int): Jumlah hari ke belakang
        
    Returns:
        str: Query untuk deteksi anomali
    """
    
    query = f'''
    // Anomaly detection for sensor data
    import "math"
    
    // Get base sensor data
    base_data = from(bucket: "{bucket}")
      |> range(start: -{days_back}d)
      |> filter(fn: (r) => r._measurement == "sensor_reading")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
      |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> keep(columns: ["_time", "temperature", "humidity", "location", "device_id"])
    
    // Calculate rolling statistics for anomaly detection
    anomaly_data = base_data
      |> map(fn: (r) => ({{
          r with
          temp_zscore: 0.0,  // Will be calculated in post-processing
          humidity_zscore: 0.0,
          temp_outlier: 0,
          humidity_outlier: 0
      }}))
    
    anomaly_data
    '''
    
    return query


def get_feature_engineering_query(bucket: str, days_back: int = 30) -> str:
    """
    Query dengan feature engineering yang lengkap
    
    Args:
        bucket (str): Nama bucket InfluxDB
        days_back (int): Jumlah hari ke belakang
        
    Returns:
        str: Query dengan features engineering
    """
    
    query = f'''
    // Advanced feature engineering query
    import "math"
    import "interpolate"
    
    // Base sensor data
    base_data = from(bucket: "{bucket}")
      |> range(start: -{days_back}d)
      |> filter(fn: (r) => r._measurement == "sensor_reading")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
      |> aggregateWindow(every: 10m, fn: mean, createEmpty: true)
      |> interpolate.linear(every: 10m)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> keep(columns: ["_time", "temperature", "humidity", "location", "device_id"])
      |> sort(columns: ["_time"])
    
    // Add moving averages and time features
    enhanced_data = base_data
      |> map(fn: (r) => ({{
          r with
          hour: int(v: date.hour(t: r._time)),
          day_of_week: int(v: date.weekDay(t: r._time)),
          month: int(v: date.month(t: r._time)),
          is_weekend: if int(v: date.weekDay(t: r._time)) >= 6 then 1 else 0,
          is_working_hours: if int(v: date.hour(t: r._time)) >= 8 and int(v: date.hour(t: r._time)) <= 17 then 1 else 0
      }}))
      |> timedMovingAverage(every: 10m, period: 1h)
      |> rename(columns: {{temperature: "temp_ma_1h", humidity: "humidity_ma_1h"}})
    
    enhanced_data
    '''
    
    return query


def get_data_quality_query(bucket: str, days_back: int = 30) -> str:
    """
    Query untuk mengecek kualitas data
    
    Args:
        bucket (str): Nama bucket InfluxDB
        days_back (int): Jumlah hari ke belakang
        
    Returns:
        str: Query untuk quality check
    """
    
    query = f'''
    // Data quality assessment query
    import "math"
    
    // Get data completeness stats
    completeness = from(bucket: "{bucket}")
      |> range(start: -{days_back}d)
      |> filter(fn: (r) => r._measurement == "sensor_reading")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
      |> group(columns: ["location", "device_id", "_field"])
      |> count()
      |> group()
      |> pivot(rowKey:["location", "device_id"], columnKey: ["_field"], valueColumn: "_value")
      |> map(fn: (r) => ({{
          location: r.location,
          device_id: r.device_id,
          temperature_count: r.temperature,
          humidity_count: r.humidity,
          completeness_score: float(v: math.min(x: r.temperature, y: r.humidity)) / float(v: math.max(x: r.temperature, y: r.humidity))
      }}))
    
    completeness
    '''
    
    return query


def get_time_series_features_query(bucket: str, days_back: int = 30, lag_hours: list = [1, 6, 24]) -> str:
    """
    Query untuk membuat time series features dengan lag
    
    Args:
        bucket (str): Nama bucket InfluxDB
        days_back (int): Jumlah hari ke belakang
        lag_hours (list): List jam untuk lag features
        
    Returns:
        str: Query dengan lag features
    """
    
    # Convert lag hours to intervals
    lag_intervals = [f"{h}h" for h in lag_hours]
    
    query = f'''
    // Time series features with lag
    import "math"
    
    base_data = from(bucket: "{bucket}")
      |> range(start: -{days_back}d)
      |> filter(fn: (r) => r._measurement == "sensor_reading")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
      |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> keep(columns: ["_time", "temperature", "humidity", "location", "device_id"])
      |> sort(columns: ["_time"])
    
    // Add rate of change features
    features_data = base_data
      |> derivative(unit: 10m, nonNegative: false, columns: ["temperature", "humidity"])
      |> rename(columns: {{temperature: "temp_rate", humidity: "humidity_rate"}})
    
    features_data
    '''
    
    return query
