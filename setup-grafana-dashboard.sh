#!/bin/bash

# Script untuk setup dashboard Grafana secara otomatis
# Menunggu sampai Grafana ready dan membuat dashboard environmental

echo "=== Setup Grafana Dashboard untuk Digital Twin ==="

# Tunggu sampai Grafana service ready
echo "Menunggu Grafana service ready..."
until $(curl --output /dev/null --silent --head --fail http://localhost:3001); do
    printf '.'
    sleep 5
done
echo ""
echo "Grafana service sudah ready!"

# Login dan dapatkan session
echo "Login ke Grafana..."
GRAFANA_URL="http://localhost:3001"
ADMIN_USER="admin"
ADMIN_PASS="padipadi"

# Create datasource InfluxDB
echo "Membuat datasource InfluxDB..."
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46cGFkaXBhZGk=" \
  -d '{
    "name": "InfluxDB",
    "type": "influxdb",
    "url": "http://influxdb:8086",
    "access": "proxy",
    "database": "sensor_data_primary",
    "user": "",
    "password": "",
    "basicAuth": false,
    "basicAuthUser": "",
    "basicAuthPassword": "",
    "withCredentials": false,
    "isDefault": true,
    "jsonData": {
      "version": "Flux",
      "organization": "iot_project_alpha",
      "defaultBucket": "sensor_data_primary",
      "maxSeries": 1000
    },
    "secureJsonData": {
      "token": "th1s_1s_a_v3ry_s3cur3_4nd_l0ng_4dm1n_t0k3n_f0r_d3v"
    }
  }' \
  "${GRAFANA_URL}/api/datasources" || echo "Datasource mungkin sudah ada"

# Create dashboard
echo "Membuat dashboard environmental..."
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46cGFkaXBhZGk=" \
  -d '{
    "dashboard": {
      "id": null,
      "uid": "environmental-dashboard",
      "title": "Environmental Monitoring",
      "tags": ["digital-twin", "environmental"],
      "timezone": "browser",
      "refresh": "30s",
      "time": {
        "from": "now-1h",
        "to": "now"
      },
      "panels": [
        {
          "id": 1,
          "title": "Temperature",
          "type": "stat",
          "targets": [
            {
              "refId": "A",
              "query": "from(bucket: \"sensor_data_primary\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"environmental_data\")\n  |> filter(fn: (r) => r[\"_field\"] == \"temperature\")\n  |> filter(fn: (r) => r[\"location\"] == \"${location}\")\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\n  |> yield(name: \"mean\")"
            }
          ],
          "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
          "fieldConfig": {
            "defaults": {
              "unit": "celsius",
              "min": 0,
              "max": 50
            }
          }
        },
        {
          "id": 2,
          "title": "Environmental Data",
          "type": "timeseries",
          "targets": [
            {
              "refId": "A",
              "query": "from(bucket: \"sensor_data_primary\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"environmental_data\")\n  |> filter(fn: (r) => r[\"_field\"] == \"temperature\" or r[\"_field\"] == \"humidity\")\n  |> filter(fn: (r) => r[\"location\"] == \"${location}\")\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\n  |> yield(name: \"mean\")"
            }
          ],
          "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
        }
      ],
      "templating": {
        "list": [
          {
            "name": "location",
            "type": "custom",
            "options": [
              {"text": "F3", "value": "F3"},
              {"text": "G5", "value": "G5"},
              {"text": "G8", "value": "G8"}
            ],
            "current": {"text": "F3", "value": "F3"}
          }
        ]
      }
    },
    "overwrite": true
  }' \
  "${GRAFANA_URL}/api/dashboards/db"

echo ""
echo "=== Dashboard Grafana berhasil dibuat! ==="
echo "URL Dashboard: http://localhost:3001/d/environmental-dashboard"
echo "Username: admin"
echo "Password: padipadi"
