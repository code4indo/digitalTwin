# Manual Flux Queries untuk Analisis Trend

Dokumentasi query Flux yang dapat digunakan langsung di query editor InfluxDB untuk analisis trend.

## Konfigurasi Dasar

- **Bucket**: `sensor_data_primary`
- **Measurement**: `sensor_reading`
- **Fields**: `temperature`, `humidity`
- **Tags**: `location`, `device_id`, dll.

## 1. Query Trend Harian Sederhana

### Temperature - 7 Hari Terakhir
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> sort(columns: ["_time"])
  |> yield(name: "daily_temperature")
```

### Humidity - 7 Hari Terakhir
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> sort(columns: ["_time"])
  |> yield(name: "daily_humidity")
```

## 2. Query dengan Statistik Lengkap

```flux
import "math"

data = from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")

// Rata-rata harian
daily_avg = data
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> sort(columns: ["_time"])
  |> yield(name: "daily_average")

// Minimum harian
daily_min = data
  |> aggregateWindow(every: 1d, fn: min, createEmpty: false)
  |> sort(columns: ["_time"])
  |> yield(name: "daily_minimum")

// Maksimum harian
daily_max = data
  |> aggregateWindow(every: 1d, fn: max, createEmpty: false)
  |> sort(columns: ["_time"])
  |> yield(name: "daily_maximum")
```

## 3. Query Moving Average

### 3-Day Moving Average
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -14d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> timedMovingAverage(every: 1d, period: 3d)
  |> sort(columns: ["_time"])
  |> yield(name: "3day_moving_average")
```

### 7-Day Moving Average
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -21d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> timedMovingAverage(every: 1d, period: 7d)
  |> sort(columns: ["_time"])
  |> yield(name: "7day_moving_average")
```

## 4. Query dengan Filter Lokasi

```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> filter(fn: (r) => r["location"] == "room_1")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> sort(columns: ["_time"])
  |> yield(name: "daily_room1_temperature")
```

## 5. Query Perbandingan Periode

### Week-to-Week Comparison
```flux
// Minggu ini
current_week = from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> mean()
  |> duplicate(column: "_value", as: "current_week_avg")
  |> yield(name: "current_week")

// Minggu sebelumnya
previous_week = from(bucket: "sensor_data_primary")
  |> range(start: -14d, stop: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> mean()
  |> duplicate(column: "_value", as: "previous_week_avg")
  |> yield(name: "previous_week")
```

## 6. Query Deteksi Anomali

```flux
import "math"

// Data periode
data = from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")

// Hitung mean dan standard deviation
stats = data
  |> duplicate(column: "_value", as: "value_copy")
  |> group()
  |> reduce(
      fn: (r, accumulator) => ({
          sum: accumulator.sum + r._value,
          count: accumulator.count + 1.0,
          sum_sq: accumulator.sum_sq + (r._value * r._value)
      }),
      identity: {sum: 0.0, count: 0.0, sum_sq: 0.0}
  )
  |> map(fn: (r) => ({
      mean: r.sum / r.count,
      variance: (r.sum_sq / r.count) - math.pow(x: r.sum / r.count, n: 2.0)
  }))
  |> map(fn: (r) => ({
      mean: r.mean,
      std_dev: math.sqrt(x: r.variance),
      upper_threshold: r.mean + (2.0 * math.sqrt(x: r.variance)),
      lower_threshold: r.mean - (2.0 * math.sqrt(x: r.variance))
  }))

// Identifikasi anomali
anomalies = data
  |> join(tables: {stats: stats}, on: [])
  |> filter(fn: (r) => r._value > r.upper_threshold or r._value < r.lower_threshold)
  |> yield(name: "anomalies")

// Return juga threshold values
stats |> yield(name: "thresholds")
```

## 7. Query Komprehensif - Dashboard Ready

```flux
import "math"

// Data utama
data = from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")

// Agregasi harian
daily_data = data
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> sort(columns: ["_time"])

// Data trend harian
daily_trend = daily_data
  |> yield(name: "daily_trend")

// Moving average 3 hari
moving_avg = daily_data
  |> timedMovingAverage(every: 1d, period: 3d)
  |> yield(name: "moving_average_3d")

// Statistik keseluruhan
overall_stats = data
  |> group()
  |> reduce(
      fn: (r, accumulator) => ({
          sum: accumulator.sum + r._value,
          count: accumulator.count + 1.0,
          min: if r._value < accumulator.min then r._value else accumulator.min,
          max: if r._value > accumulator.max then r._value else accumulator.max
      }),
      identity: {sum: 0.0, count: 0.0, min: 999.0, max: -999.0}
  )
  |> map(fn: (r) => ({
      _time: now(),
      average: r.sum / r.count,
      minimum: r.min,
      maximum: r.max,
      range: r.max - r.min
  }))
  |> yield(name: "overall_statistics")
```

## Tips Penggunaan

1. **Ganti periode**: Ubah `-7d` menjadi `-30d` untuk data bulanan
2. **Ganti parameter**: Ubah `"temperature"` menjadi `"humidity"` untuk data kelembaban
3. **Filter lokasi**: Tambahkan `|> filter(fn: (r) => r["location"] == "room_name")`
4. **Agregasi berbeda**: Ganti `fn: mean` dengan `fn: max`, `fn: min`, atau `fn: median`

## Contoh Hasil Query

Query akan menghasilkan tabel dengan kolom:
- `_time`: Timestamp
- `_value`: Nilai pengukuran
- `_field`: Parameter (temperature/humidity)
- `location`: Lokasi sensor (jika ada)

Untuk dashboard, gunakan kolom `_time` sebagai sumbu X dan `_value` sebagai sumbu Y.
