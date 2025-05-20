// Ambil data temperatur
temp_series = from(bucket: "sensor_data_primary")
  |> range(start: -24h) // Sesuaikan rentang waktu jika perlu
  |> filter(fn: (r) => r._measurement == "bmkg_weather_forecast")
  |> filter(fn: (r) => r.kode_wilayah == "31.74.04.1003") // Menggunakan kode wilayah yang benar
  |> filter(fn: (r) => r._field == "temperature")
  // Kelompokkan agar semua data temperatur untuk kode_wilayah ini menjadi satu series
  |> group(columns: ["_measurement", "kode_wilayah", "source", "_field"])
  |> sort(columns: ["_time"])

// Ambil data kelembapan
humidity_series = from(bucket: "sensor_data_primary")
  |> range(start: -24h) // Sesuaikan rentang waktu jika perlu
  |> filter(fn: (r) => r._measurement == "bmkg_weather_forecast")
  |> filter(fn: (r) => r.kode_wilayah == "31.74.04.1003") // Menggunakan kode wilayah yang benar
  |> filter(fn: (r) => r._field == "humidity")
  // Kelompokkan agar semua data kelembapan untuk kode_wilayah ini menjadi satu series
  |> group(columns: ["_measurement", "kode_wilayah", "source", "_field"])
  |> sort(columns: ["_time"])

// Gabungkan kedua series tersebut
union(tables: [temp_series, humidity_series])
  |> yield(name: "grafik_suhu_dan_kelembapan")
