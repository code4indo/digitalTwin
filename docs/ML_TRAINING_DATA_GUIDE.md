# Panduan Pengumpulan Data Training untuk Model Machine Learning Digital Twin

## Overview

Sistem Digital Twin menggunakan data historis dari InfluxDB sebagai sumber utama untuk training model machine learning prediktif. Data ini mencakup pembacaan sensor internal, data cuaca eksternal, dan berbagai metadata yang diperlukan untuk membuat prediksi yang akurat.

## Sumber Data

### 1. Data Sensor Internal (Primary Source)
- **Measurement**: `sensor_reading`
- **Fields**: `temperature`, `humidity`
- **Tags**: `device_id`, `location`, `source_ip`
- **Interval**: 10 detik (dikonfigurasi di Telegraf)
- **Storage**: InfluxDB bucket `sensor_data_primary`

### 2. Data Cuaca Eksternal (Secondary Source)
- **Measurement**: `bmkg_weather`
- **Fields**: `temperature`, `humidity`, `weather_code`
- **Source**: BMKG API via collector script
- **Interval**: 1 jam
- **Storage**: InfluxDB bucket `sensor_data_primary`

## Struktur Data Training

### Raw Data Schema
```
timestamp, device_id, location, temperature, humidity, outdoor_temp, outdoor_humidity, weather_code
```

### Engineered Features
```
- Basic Features: temperature, humidity, hour, day_of_week, month, is_weekend
- Lag Features: temp_lag_1h, humidity_lag_1h, temp_lag_6h, humidity_lag_6h  
- Moving Averages: temp_ma_1h, humidity_ma_1h, temp_ma_6h, humidity_ma_6h
- Rate of Change: temp_change_rate, humidity_change_rate
- External Features: outdoor_temp, outdoor_humidity, temp_diff_indoor_outdoor
```

### Target Variables
```
- temp_target: Temperature 1 hour ahead
- humidity_target: Humidity 1 hour ahead
```

## Cara Mengumpulkan Data Training

### 1. Menggunakan Service Langsung

```python
from services.ml_training_service import create_training_data_collector

# Create collector instance
collector = create_training_data_collector()

# Collect historical data
data = await collector.collect_historical_data(
    days_back=30,
    location_filter="F2",  # Optional: filter by location
    device_filter="2D3032"  # Optional: filter by device
)

# Prepare features and targets
features, targets = await collector.prepare_training_features(data)

# Save to file
await collector.save_training_data(features, targets, "training_data.csv")
```

### 2. Menggunakan Script Command Line

```bash
# Basic collection (30 days, all locations)
python collect_training_data.py

# With specific parameters
python collect_training_data.py --days 60 --location F2 --output-dir /data/training

# Without external weather data
python collect_training_data.py --days 30 --no-external

# With device filter
python collect_training_data.py --days 45 --device 2D3032 --output-file custom_training.csv
```

### 3. Menggunakan API Endpoints

```bash
# Get training data statistics
curl -H "X-API-Key: development_key_for_testing" \
  "http://localhost:8002/ml/training-data/stats?days_back=30"

# Collect training data
curl -H "X-API-Key: development_key_for_testing" \
  "http://localhost:8002/ml/training-data/collect?days_back=30&save_to_file=true"

# Get sample data for testing
curl -H "X-API-Key: development_key_for_testing" \
  "http://localhost:8002/ml/data/sample?limit=100"
```

## Konfigurasi Data Collection

### Environment Variables
```bash
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v
INFLUXDB_ORG=iot_project_alpha
INFLUXDB_BUCKET_PRIMARY=sensor_data_primary
```

### Data Quality Requirements
- **Minimum Records**: 1000 samples untuk training
- **Time Range**: Minimal 7 hari untuk deteksi pola
- **Completeness**: >90% data tidak boleh missing
- **Outlier Threshold**: Z-score > 3 dianggap outlier

## Optimasi Query Flux

### Query Dasar untuk Training Data
```flux
from(bucket: "sensor_data_primary")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: true)
  |> interpolate.linear(every: 10m)
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"])
```

### Query dengan Feature Engineering
```flux
// Lihat file flux_queries/ml_training_queries.py untuk queries lengkap
```

## Data Pipeline Flow

```
1. Sensor Hardware → Telegraf → InfluxDB (Raw Data)
2. BMKG API → Data Collector → InfluxDB (External Data)
3. InfluxDB → ML Training Service → Feature Engineering
4. Engineered Features → CSV/Parquet → ML Model Training
5. Trained Model → Prediction API → Frontend Dashboard
```

## Testing dan Validasi

### Test Data Collection
```bash
# Run test script
python test_ml_training_data.py

# Check API endpoints
curl -H "X-API-Key: development_key_for_testing" \
  "http://localhost:8002/ml/training-data/stats"
```

### Validasi Data Quality
```python
# Check data completeness
data_stats = await collector.collect_historical_data(days_back=7)
missing_temp = data_stats['temperature'].isna().sum()
missing_humidity = data_stats['humidity'].isna().sum()
completeness = (1 - missing_values / len(data_stats)) * 100
```

## Troubleshooting

### Common Issues

1. **No Data Found**
   - Check InfluxDB connection
   - Verify bucket name and organization
   - Ensure Telegraf is collecting data
   - Check time range parameters

2. **Missing External Data**
   - Verify BMKG data collector is running
   - Check network connectivity to BMKG API
   - Review data collector logs

3. **Poor Data Quality**
   - Check sensor connectivity
   - Review Telegraf configuration
   - Validate data ingestion pipeline

4. **Large Dataset Performance**
   - Use time-based filtering
   - Implement data sampling
   - Optimize Flux queries

### Performance Tips

1. **Query Optimization**
   - Use specific time ranges
   - Filter by location/device early
   - Use aggregateWindow for large datasets

2. **Memory Management**
   - Process data in chunks
   - Use streaming for large datasets
   - Implement data pagination

3. **Storage Optimization**
   - Use appropriate data retention policies
   - Implement data compression
   - Regular cleanup of old data

## File Output Format

### CSV Structure
```csv
timestamp,temperature,humidity,hour,day_of_week,month,is_weekend,temp_lag_1h,humidity_lag_1h,temp_ma_1h,humidity_ma_1h,temp_target,humidity_target
2025-06-10T10:00:00Z,23.5,65.2,10,1,6,0,23.2,64.8,23.3,65.0,23.8,65.5
```

### Metadata JSON
```json
{
  "generation_time": "2025-06-10T15:30:00Z",
  "days_back": 30,
  "total_samples": 4320,
  "feature_count": 15,
  "target_count": 2,
  "date_range": {
    "start": "2025-05-11T15:30:00Z",
    "end": "2025-06-10T15:30:00Z"
  },
  "data_quality": {
    "missing_values": 0,
    "completeness": 100.0
  }
}
```

## Next Steps

1. **Model Training**: Gunakan data CSV untuk melatih model ML
2. **Model Deployment**: Deploy model ke prediction API
3. **Continuous Learning**: Setup pipeline untuk retrain model
4. **Monitoring**: Implement model performance monitoring
