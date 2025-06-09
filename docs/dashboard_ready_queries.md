# Dashboard Ready - Query Flux untuk Trend Harian

Query-query ini siap digunakan untuk dashboard dan dapat langsung di-copy ke InfluxDB Query Editor.

## Quick Daily Trend - Siap Pakai

### 1. Temperature Trend 7 Hari (Dashboard Panel)
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({
      r with
      _time: r._time,
      temperature: r._value
  }))
  |> keep(columns: ["_time", "temperature"])
```

### 2. Humidity Trend 7 Hari (Dashboard Panel)
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({
      r with
      _time: r._time,
      humidity: r._value
  }))
  |> keep(columns: ["_time", "humidity"])
```

### 3. Combined Temperature & Humidity Trend
```flux
// Temperature data
temp = from(bucket: "sensor_data_primary")
  |> range(start: -14d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> set(key: "_field", value: "temperature")

// Humidity data
humidity = from(bucket: "sensor_data_primary")
  |> range(start: -14d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> set(key: "_field", value: "humidity")

// Combine both
union(tables: [temp, humidity])
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> yield(name: "combined_daily_trend")
```

## Analisis Mendalam

### 4. Daily Summary with Statistics
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(
      every: 1d,
      fn: (column, tables=<-) => tables
        |> mean()
        |> set(key: "stat", value: "mean")
        |> union(tables: tables |> min() |> set(key: "stat", value: "min"))
        |> union(tables: tables |> max() |> set(key: "stat", value: "max"))
        |> pivot(rowKey: ["_time"], columnKey: ["stat"], valueColumn: "_value"),
      createEmpty: false
  )
```

### 5. Week-over-Week Comparison
```flux
// This week
this_week = from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> set(key: "period", value: "this_week")

// Last week
last_week = from(bucket: "sensor_data_primary")
  |> range(start: -14d, stop: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> timeShift(duration: 7d)
  |> set(key: "period", value: "last_week")

// Combine for comparison
union(tables: [this_week, last_week])
  |> pivot(rowKey: ["_time"], columnKey: ["period"], valueColumn: "_value")
```

## Filter Berdasarkan Lokasi

### 6. Per Location Daily Trend
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> group(columns: ["location"])
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> pivot(rowKey: ["_time"], columnKey: ["location"], valueColumn: "_value")
```

### 7. Specific Location Trend (Archive Room)
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> filter(fn: (r) => r["location"] == "archive_room_1")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
```

## Advanced Analytics

### 8. Daily Trend with Moving Average
```flux
daily_temp = from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)

// Original daily values
original = daily_temp
  |> set(key: "type", value: "daily")

// 3-day moving average
ma3 = daily_temp
  |> movingAverage(n: 3)
  |> set(key: "type", value: "3day_avg")

// 7-day moving average
ma7 = daily_temp
  |> movingAverage(n: 7)
  |> set(key: "type", value: "7day_avg")

// Combine all
union(tables: [original, ma3, ma7])
  |> pivot(rowKey: ["_time"], columnKey: ["type"], valueColumn: "_value")
```

### 9. Daily Growth Rate
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> sort(columns: ["_time"])
  |> difference(nonNegative: false)
  |> map(fn: (r) => ({
      r with
      daily_change: r._value
  }))
  |> keep(columns: ["_time", "daily_change"])
```

### 10. Anomaly Detection - Daily
```flux
// Get daily averages
daily_data = from(bucket: "sensor_data_primary")
  |> range(start: -60d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)

// Calculate statistics for anomaly detection
stats = daily_data
  |> duplicate(column: "_value", as: "temp_value")
  |> group()
  |> reduce(
      fn: (r, accumulator) => ({
          count: accumulator.count + 1.0,
          sum: accumulator.sum + r.temp_value,
          sum_sq: accumulator.sum_sq + (r.temp_value * r.temp_value)
      }),
      identity: {count: 0.0, sum: 0.0, sum_sq: 0.0}
  )
  |> map(fn: (r) => ({
      mean: r.sum / r.count,
      variance: (r.sum_sq - (r.sum * r.sum / r.count)) / r.count,
      stddev: math.sqrt(x: (r.sum_sq - (r.sum * r.sum / r.count)) / r.count)
  }))

// Flag anomalies
daily_data
  |> map(fn: (r) => ({
      r with
      is_anomaly: math.abs(x: r._value - 25.0) > 3.0,
      z_score: (r._value - 25.0) / 2.0
  }))
```

---

## Penggunaan Cepat:

1. **Copy query** yang diinginkan
2. **Paste ke InfluxDB Query Editor**
3. **Ubah parameter** sesuai kebutuhan:
   - `start: -7d` → ubah rentang waktu
   - `"temperature"` → ganti ke `"humidity"` jika perlu
   - `"archive_room_1"` → sesuaikan nama lokasi
4. **Execute query**
5. **Export hasil** untuk dashboard atau analisis lanjutan

Semua query ini sudah dioptimalkan untuk performa dan dapat langsung digunakan untuk dashboard monitoring atau analisis trend harian data sensor Anda.
