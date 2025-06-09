# Simple Flux Query - Copy & Paste Ready

Query sederhana yang bisa langsung di-copy paste ke InfluxDB Query Editor untuk melihat trend harian.

---

## 🔥 QUERY PALING SERING DIGUNAKAN

### ➡️ Temperature 7 Hari Terakhir
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1d, fn: mean)
```

### ➡️ Humidity 7 Hari Terakhir
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "humidity")
  |> aggregateWindow(every: 1d, fn: mean)
```

### ➡️ Temperature Hari Ini Saja
```flux
from(bucket: "sensor_data_primary")
  |> range(start: today())
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1h, fn: mean)
```

---

## 📊 ANALISIS TREND

### ➡️ Temperature Min/Max/Average Harian (30 hari)
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1d, fn: mean)
  |> duplicate(column: "_value", as: "avg")
  |> map(fn: (r) => ({r with avg: r._value}))
```

### ➡️ Perbandingan Temperature vs Humidity (14 hari)
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -14d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
  |> aggregateWindow(every: 1d, fn: mean)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
```

### ➡️ Moving Average 3 Hari
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1d, fn: mean)
  |> movingAverage(n: 3)
```

---

## 🏢 FILTER BERDASARKAN LOKASI

### ➡️ Temperature di Archive Room 1
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> filter(fn: (r) => r.location == "archive_room_1")
  |> aggregateWindow(every: 1d, fn: mean)
```

### ➡️ Semua Lokasi dalam 1 Query
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> group(columns: ["location"])
  |> aggregateWindow(every: 1d, fn: mean)
```

---

## ⏰ RENTANG WAKTU BERBEDA

### ➡️ Data 24 Jam Terakhir (per jam)
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1h, fn: mean)
```

### ➡️ Data Minggu Ini
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -1w)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1d, fn: mean)
```

### ➡️ Data Bulan Ini
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1d, fn: mean)
```

---

## 📈 STATISTIK SEDERHANA

### ➡️ Rata-rata Mingguan
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -8w)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1w, fn: mean)
```

### ➡️ Temperature Tertinggi dan Terendah Hari Ini
```flux
from(bucket: "sensor_data_primary")
  |> range(start: today())
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature")
  |> group()
  |> reduce(
      fn: (r, accumulator) => ({
          max_temp: if r._value > accumulator.max_temp then r._value else accumulator.max_temp,
          min_temp: if r._value < accumulator.min_temp then r._value else accumulator.min_temp
      }),
      identity: {max_temp: -999.0, min_temp: 999.0}
  )
```

---

## 🔍 TROUBLESHOOTING

Jika query tidak mengembalikan data, coba query ini untuk cek data yang tersedia:

### ➡️ Cek Measurement yang Ada
```flux
import "influxdata/influxdb/schema"
schema.measurements(bucket: "sensor_data_primary")
```

### ➡️ Cek Field yang Ada
```flux
import "influxdata/influxdb/schema"
schema.fieldKeys(bucket: "sensor_data_primary", measurement: "sensor_reading")
```

### ➡️ Cek Tag yang Ada
```flux
import "influxdata/influxdb/schema"
schema.tagKeys(bucket: "sensor_data_primary", measurement: "sensor_reading")
```

### ➡️ Cek Data Terbaru
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> limit(n: 10)
```

---

## 💡 TIPS PENGGUNAAN

1. **Copy-paste** query yang diinginkan ke InfluxDB Query Editor
2. **Ubah parameter** sesuai kebutuhan:
   - `-7d` → `-1d`, `-30d`, `-1h`, dsb
   - `temperature` → `humidity`
   - `every: 1d` → `every: 1h`, `every: 6h`, dsb
3. **Klik Submit** untuk menjalankan
4. **Switch ke Graph** untuk melihat visualisasi trend

**URL InfluxDB**: http://localhost:8086
