# Query Flux untuk Analisis Trend Harian - InfluxDB Query Editor

Kumpulan query Flux yang dapat digunakan langsung di query editor InfluxDB untuk analisis trend harian data sensor.

## Konfigurasi Dasar
- **Bucket**: `sensor_data_primary`
- **Measurement**: `sensor_reading`
- **Fields**: `temperature`, `humidity`
- **Tags**: `location`, `device_id`

---

## 1. Trend Harian Temperature - 7 Hari Terakhir

```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> yield(name: "daily_temperature_trend")
```

## 2. Trend Harian Temperature dengan Min/Max - 30 Hari

```flux
// Average temperature per day
temp_avg = from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> set(key: "metric", value: "avg")

// Minimum temperature per day
temp_min = from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: min, createEmpty: false)
  |> set(key: "metric", value: "min")

// Maximum temperature per day
temp_max = from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: max, createEmpty: false)
  |> set(key: "metric", value: "max")

// Combine all metrics
union(tables: [temp_avg, temp_min, temp_max])
  |> pivot(rowKey: ["_time"], columnKey: ["metric"], valueColumn: "_value")
  |> yield(name: "daily_temperature_minmaxavg")
```

## 3. Trend Harian Humidity - 14 Hari Terakhir

```flux
from(bucket: "sensor_data_primary")
  |> range(start: -14d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> yield(name: "daily_humidity_trend")
```

## 4. Trend Harian Temperature per Lokasi - 7 Hari

```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> group(columns: ["location"])
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> yield(name: "daily_temperature_by_location")
```

## 5. Trend Harian dengan Moving Average (3 hari)

```flux
from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> movingAverage(n: 3)
  |> yield(name: "daily_temperature_3day_moving_avg")
```

## 6. Perbandingan Trend Harian Temperature vs Humidity

```flux
// Daily temperature
temp_daily = from(bucket: "sensor_data_primary")
  |> range(start: -14d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> set(key: "sensor_type", value: "temperature")

// Daily humidity
humidity_daily = from(bucket: "sensor_data_primary")
  |> range(start: -14d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "humidity")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> set(key: "sensor_type", value: "humidity")

// Combine both
union(tables: [temp_daily, humidity_daily])
  |> yield(name: "daily_temp_humidity_comparison")
```

## 7. Trend Harian dengan Deteksi Anomali

```flux
// Calculate daily mean and standard deviation
daily_stats = from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)

// Calculate overall statistics for anomaly detection
overall_mean = daily_stats
  |> mean()
  |> findColumn(fn: (key) => true, column: "_value")
  |> getRecord(idx: 0)

overall_stddev = daily_stats
  |> stddev()
  |> findColumn(fn: (key) => true, column: "_value")
  |> getRecord(idx: 0)

// Flag anomalies (values beyond 2 standard deviations)
daily_stats
  |> map(fn: (r) => ({
      r with
      is_anomaly: if math.abs(x: r._value - overall_mean._value) > 2.0 * overall_stddev._value then true else false,
      deviation: (r._value - overall_mean._value) / overall_stddev._value
  }))
  |> yield(name: "daily_temperature_with_anomalies")
```

## 8. Trend Harian dengan Filter Jam Kerja (08:00-17:00)

```flux
from(bucket: "sensor_data_primary")
  |> range(start: -14d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> filter(fn: (r) => {
      hour = date.hour(t: r._time)
      return hour >= 8 and hour <= 17
  })
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> yield(name: "daily_temperature_working_hours")
```

## 9. Weekly Trend (Trend Mingguan)

```flux
from(bucket: "sensor_data_primary")
  |> range(start: -8w)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1w, fn: mean, createEmpty: false)
  |> yield(name: "weekly_temperature_trend")
```

## 10. Trend Harian dengan Persentase Perubahan

```flux
daily_temp = from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> sort(columns: ["_time"])

daily_temp
  |> difference(nonNegative: false, columns: ["_value"])
  |> map(fn: (r) => ({
      r with
      percent_change: if r._value != 0.0 then (r._value / (r._value - r._value)) * 100.0 else 0.0
  }))
  |> yield(name: "daily_temperature_change_percent")
```

---

## Cara Penggunaan:

1. **Buka InfluxDB UI** di browser: `http://localhost:8086`
2. **Login** dengan kredensial yang ada di docker-compose.yml
3. **Buka Data Explorer** atau **Query Editor**
4. **Copy-paste** salah satu query di atas
5. **Klik Submit/Execute** untuk menjalankan query
6. **Lihat hasil** dalam bentuk tabel atau grafik

## Tips:

- Ubah parameter `start:` untuk menyesuaikan rentang waktu (contoh: `-1d`, `-7d`, `-30d`)
- Sesuaikan `every:` pada `aggregateWindow()` untuk interval yang berbeda (`1h`, `6h`, `1d`, `1w`)
- Tambahkan filter lokasi dengan: `|> filter(fn: (r) => r["location"] == "archive_room_1")`
- Gunakan `yield(name: "custom_name")` untuk memberi nama hasil query

## Troubleshooting:

Jika query tidak mengembalikan data:
1. Periksa nama bucket: `sensor_data_primary`
2. Periksa nama measurement: `sensor_reading`
3. Periksa nama field: `temperature`, `humidity`
4. Pastikan ada data dalam rentang waktu yang dipilih
5. Cek tag yang tersedia dengan query: `show tag keys from "sensor_reading"`
