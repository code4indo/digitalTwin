# Dokumentasi API Endpoint Statistik Lingkungan

## Endpoint Statistik Suhu

```
GET /stats/temperature/
```

Endpoint ini mengembalikan statistik suhu (rata-rata, minimum, maksimum) dari seluruh perangkat yang dimonitor. Data dapat difilter berdasarkan rentang waktu dan lokasi.

### Parameter Query
- `start_time`: Waktu mulai (format ISO, cth: 2023-01-01T00:00:00Z). Default: 24 jam terakhir.
- `end_time`: Waktu selesai (format ISO, cth: 2023-01-01T01:00:00Z). Default: sekarang.
- `locations`: Daftar lokasi untuk difilter. Dapat menentukan multiple lokasi.

### Respon

```json
{
  "avg_temperature": 25.5,
  "min_temperature": 22.0,
  "max_temperature": 29.0,
  "sample_count": 720
}
```

## Endpoint Statistik Kelembapan

```
GET /stats/humidity/
```

Endpoint ini mengembalikan statistik kelembapan (rata-rata, minimum, maksimum) dari seluruh perangkat yang dimonitor. Data dapat difilter berdasarkan rentang waktu dan lokasi.

### Parameter Query
- `start_time`: Waktu mulai (format ISO, cth: 2023-01-01T00:00:00Z). Default: 24 jam terakhir.
- `end_time`: Waktu selesai (format ISO, cth: 2023-01-01T01:00:00Z). Default: sekarang.
- `locations`: Daftar lokasi untuk difilter. Dapat menentukan multiple lokasi.

### Respon

```json
{
  "avg_humidity": 65,
  "min_humidity": 50,
  "max_humidity": 80,
  "sample_count": 720
}
```

## Endpoint Statistik Lingkungan (Gabungan)

```
GET /stats/environmental/
```

Endpoint ini mengembalikan statistik suhu dan kelembapan (rata-rata, minimum, maksimum) dari seluruh perangkat yang dimonitor dalam satu respon. Data dapat difilter berdasarkan rentang waktu dan lokasi.

### Parameter Query
- `start_time`: Waktu mulai (format ISO, cth: 2023-01-01T00:00:00Z). Default: 24 jam terakhir.
- `end_time`: Waktu selesai (format ISO, cth: 2023-01-01T01:00:00Z). Default: sekarang.
- `locations`: Daftar lokasi untuk difilter. Dapat menentukan multiple lokasi.

### Respon

```json
{
  "temperature": {
    "avg": 25.5,
    "min": 22.0,
    "max": 29.0,
    "sample_count": 720
  },
  "humidity": {
    "avg": 65,
    "min": 50,
    "max": 80,
    "sample_count": 720
  },
  "timestamp": "2025-05-21T12:30:45.123456"
}
```

## Endpoint Data Ruangan

### Daftar Ruangan

```
GET /rooms/
```

Endpoint ini mengembalikan daftar semua ruangan yang tersedia dengan metadata dasar.

### Respon

```json
[
  {
    "id": "F2",
    "name": "Ruang F2",
    "floor": "F",
    "area": 25
  },
  {
    "id": "G3",
    "name": "Ruang G3",
    "floor": "G",
    "area": 30
  }
]
```

### Detail Ruangan

```
GET /rooms/{room_id}
```

Endpoint ini mengembalikan data detail ruangan tertentu, termasuk kondisi lingkungan terkini dan informasi perangkat.

### Parameter Path
- `room_id`: ID ruangan (contoh: F2, G3, dsb)

### Respon

```json
{
  "id": "F2",
  "name": "Ruang F2",
  "floor": "F",
  "area": 25,
  "currentConditions": {
    "temperature": 22.5,
    "humidity": 50.0,
    "co2": 450,
    "light": 400
  },
  "statistics": {
    "dailyAvg": {
      "temperature": 22.0,
      "humidity": 48.0
    },
    "timeInOptimalRange": {
      "temperature": 85,
      "humidity": 70
    }
  },
  "devices": [
    {
      "id": "ac-f2",
      "name": "AC",
      "status": "active",
      "setPoint": 21
    },
    {
      "id": "dh-f2",
      "name": "Dehumidifier",
      "status": "active",
      "setPoint": 50
    }
  ]
}
```

## Catatan Penggunaan

1. Semua endpoint memerlukan autentikasi API Key melalui header `X-API-Key`.
2. Nilai suhu diformat dengan satu angka desimal (contoh: 25.5°C).
3. Nilai kelembapan diformat sebagai bilangan bulat (contoh: 65%).
4. Jika tidak ada data yang ditemukan, nilai akan dikembalikan sebagai `null`.
5. Parameter `locations` mendukung multiple nilai, contoh: `?locations=R.Arsip-1&locations=R.Arsip-2`
