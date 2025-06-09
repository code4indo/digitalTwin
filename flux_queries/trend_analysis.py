"""
Flux queries untuk analisis tren temporal data sensor
"""

def get_hourly_aggregated_query(bucket: str, parameter: str, location_filter: str = "", hours: int = 24) -> str:
    """
    Query untuk mengambil data agregasi per jam
    
    Args:
        bucket: Nama bucket InfluxDB
        parameter: Parameter sensor ('temperature' atau 'humidity')
        location_filter: Filter lokasi tambahan
        hours: Jumlah jam data yang diambil
    
    Returns:
        String query Flux
    """
    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -{hours}h)
        |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
        |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
        |> sort(columns: ["_time"])
        |> yield(name: "hourly_data")
    '''
    return query


def get_daily_aggregated_query(bucket: str, parameter: str, location_filter: str = "", days: int = 7) -> str:
    """
    Query untuk mengambil data agregasi per hari
    
    Args:
        bucket: Nama bucket InfluxDB
        parameter: Parameter sensor ('temperature' atau 'humidity')
        location_filter: Filter lokasi tambahan
        days: Jumlah hari data yang diambil
    
    Returns:
        String query Flux
    """
    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -{days}d)
        |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
        |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
        |> sort(columns: ["_time"])
        |> yield(name: "daily_data")
    '''
    return query


def get_statistical_summary_query(bucket: str, parameter: str, location_filter: str = "", period: str = "24h") -> str:
    """
    Query untuk mengambil ringkasan statistik periode tertentu
    
    Args:
        bucket: Nama bucket InfluxDB
        parameter: Parameter sensor ('temperature' atau 'humidity')
        location_filter: Filter lokasi tambahan
        period: Periode untuk analisis (e.g., "24h", "7d", "30d")
    
    Returns:
        String query Flux untuk ringkasan statistik
    """
    query = f'''
    import "math"
    
    data = from(bucket: "{bucket}")
        |> range(start: -{period})
        |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
    
    // Hitung rata-rata
    avg_value = data
        |> mean()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "average"}})
        |> yield(name: "average")
    
    // Hitung minimum
    min_value = data
        |> min()
        |> keep(columns: ["_value", "_time"])
        |> rename(columns: {{"_value": "minimum"}})
        |> yield(name: "minimum")
    
    // Hitung maksimum
    max_value = data
        |> max()
        |> keep(columns: ["_value", "_time"])
        |> rename(columns: {{"_value": "maximum"}})
        |> yield(name: "maximum")
    
    // Hitung standar deviasi
    std_dev = data
        |> stddev()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "std_deviation"}})
        |> yield(name: "std_deviation")
    
    // Hitung jumlah data points
    count_points = data
        |> count()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "count"}})
        |> yield(name: "count")
    '''
    return query


def get_moving_average_query(bucket: str, parameter: str, location_filter: str = "", window_size: int = 3, period: str = "24h") -> str:
    """
    Query untuk menghitung moving average
    
    Args:
        bucket: Nama bucket InfluxDB
        parameter: Parameter sensor ('temperature' atau 'humidity')
        location_filter: Filter lokasi tambahan
        window_size: Ukuran window untuk moving average
        period: Periode untuk analisis
    
    Returns:
        String query Flux untuk moving average
    """
    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -{period})
        |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
        |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
        |> timedMovingAverage(every: 1h, period: {window_size}h)
        |> sort(columns: ["_time"])
        |> yield(name: "moving_average")
    '''
    return query


def get_anomaly_detection_query(bucket: str, parameter: str, location_filter: str = "", period: str = "7d", threshold_multiplier: float = 2.0) -> str:
    """
    Query untuk deteksi anomali berdasarkan standard deviation
    
    Args:
        bucket: Nama bucket InfluxDB
        parameter: Parameter sensor ('temperature' atau 'humidity')
        location_filter: Filter lokasi tambahan
        period: Periode untuk analisis
        threshold_multiplier: Multiplier untuk threshold (default 2.0 = 2 sigma)
    
    Returns:
        String query Flux untuk deteksi anomali
    """
    query = f'''
    import "math"
    
    // Ambil data periode
    data = from(bucket: "{bucket}")
        |> range(start: -{period})
        |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
    
    // Hitung mean dan std
    stats = data
        |> duplicate(column: "_value", as: "value_copy")
        |> group()
        |> reduce(
            fn: (r, accumulator) => ({{
                sum: accumulator.sum + r._value,
                count: accumulator.count + 1.0,
                sum_sq: accumulator.sum_sq + (r._value * r._value)
            }}),
            identity: {{sum: 0.0, count: 0.0, sum_sq: 0.0}}
        )
        |> map(fn: (r) => ({{
            mean: r.sum / r.count,
            variance: (r.sum_sq / r.count) - math.pow(x: r.sum / r.count, n: 2.0)
        }}))
        |> map(fn: (r) => ({{
            mean: r.mean,
            std_dev: math.sqrt(x: r.variance),
            upper_threshold: r.mean + ({threshold_multiplier} * math.sqrt(x: r.variance)),
            lower_threshold: r.mean - ({threshold_multiplier} * math.sqrt(x: r.variance))
        }}))
    
    // Identifikasi anomali
    anomalies = data
        |> join(tables: {{stats: stats}}, on: [])
        |> filter(fn: (r) => r._value > r.upper_threshold or r._value < r.lower_threshold)
        |> map(fn: (r) => ({{
            _time: r._time,
            _value: r._value,
            deviation: if r._value > r.upper_threshold 
                then r._value - r.upper_threshold 
                else r.lower_threshold - r._value,
            type: if r._value > r.upper_threshold then "high" else "low"
        }}))
        |> yield(name: "anomalies")
    
    // Return juga threshold values
    stats |> yield(name: "thresholds")
    '''
    return query


def get_peak_valley_detection_query(bucket: str, parameter: str, location_filter: str = "", period: str = "24h") -> str:
    """
    Query untuk deteksi peak dan valley dalam data
    
    Args:
        bucket: Nama bucket InfluxDB
        parameter: Parameter sensor ('temperature' atau 'humidity')
        location_filter: Filter lokasi tambahan
        period: Periode untuk analisis
    
    Returns:
        String query Flux untuk deteksi peak/valley
    """
    query = f'''
    data = from(bucket: "{bucket}")
        |> range(start: -{period})
        |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
        |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
        |> sort(columns: ["_time"])
    
    // Identifikasi peaks (local maxima)
    peaks = data
        |> window(every: 3h, period: 3h)
        |> max()
        |> duplicate(column: "_value", as: "peak_value")
        |> yield(name: "peaks")
    
    // Identifikasi valleys (local minima)
    valleys = data
        |> window(every: 3h, period: 3h)
        |> min()
        |> duplicate(column: "_value", as: "valley_value")
        |> yield(name: "valleys")
    '''
    return query


def get_trend_direction_query(bucket: str, parameter: str, location_filter: str = "", period: str = "24h") -> str:
    """
    Query untuk menentukan arah tren menggunakan linear regression sederhana
    
    Args:
        bucket: Nama bucket InfluxDB
        parameter: Parameter sensor ('temperature' atau 'humidity')
        location_filter: Filter lokasi tambahan
        period: Periode untuk analisis
    
    Returns:
        String query Flux untuk analisis arah tren
    """
    query = f'''
    import "math"
    
    data = from(bucket: "{bucket}")
        |> range(start: -{period})
        |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
        |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
        |> sort(columns: ["_time"])
    
    // Hitung first dan last values untuk simple trend
    first_value = data
        |> first()
        |> keep(columns: ["_value", "_time"])
        |> rename(columns: {{"_value": "first_value"}})
        |> yield(name: "first_value")
    
    last_value = data
        |> last()
        |> keep(columns: ["_value", "_time"])
        |> rename(columns: {{"_value": "last_value"}})
        |> yield(name: "last_value")
    
    // Hitung rate of change
    trend_data = data
        |> difference()
        |> mean()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "avg_rate_of_change"}})
        |> yield(name: "trend_direction")
    '''
    return query


def get_comparative_period_query(bucket: str, parameter: str, location_filter: str = "", current_period: str = "7d", offset_period: str = "7d") -> str:
    """
    Query untuk membandingkan periode saat ini dengan periode sebelumnya
    
    Args:
        bucket: Nama bucket InfluxDB
        parameter: Parameter sensor ('temperature' atau 'humidity')
        location_filter: Filter lokasi tambahan
        current_period: Periode saat ini
        offset_period: Offset untuk periode pembanding
    
    Returns:
        String query Flux untuk perbandingan periode
    """
    query = f'''
    // Data periode saat ini
    current_data = from(bucket: "{bucket}")
        |> range(start: -{current_period})
        |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
        |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
        |> mean()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "current_avg"}})
        |> yield(name: "current_period")
    
    // Data periode sebelumnya
    previous_data = from(bucket: "{bucket}")
        |> range(start: -{int(current_period[:-1]) + int(offset_period[:-1])}d, stop: -{current_period})
        |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
        |> filter(fn: (r) => r["_field"] == "{parameter}")
        {location_filter}
        |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
        |> mean()
        |> keep(columns: ["_value"])
        |> rename(columns: {{"_value": "previous_avg"}})
        |> yield(name: "previous_period")
    '''
    return query
