import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timezone

# Impor aplikasi FastAPI Anda dan variabel lain yang mungkin dibutuhkan
# Pastikan PYTHONPATH diatur dengan benar jika menjalankan dari direktori lain
from api import app, INFLUXDB_BUCKET, ALLOWED_AGGREGATE_FUNCTIONS

# Kunci API yang valid untuk digunakan dalam testing
TEST_API_KEY = "test_secret_key_123"
INVALID_API_KEY = "invalid_key_456"

@pytest.fixture(scope="module")
def client():
    """
    Fixture untuk menyediakan instance TestClient.
    Ini juga mengatur environment variable untuk API key selama tes.
    """
    original_valid_keys = os.environ.get("VALID_API_KEYS")
    original_skip_check = os.environ.get("SKIP_API_KEY_CHECK_FOR_DEV")

    os.environ["VALID_API_KEYS"] = TEST_API_KEY
    # Pastikan SKIP_API_KEY_CHECK_FOR_DEV tidak aktif agar autentikasi diuji
    if "SKIP_API_KEY_CHECK_FOR_DEV" in os.environ:
        del os.environ["SKIP_API_KEY_CHECK_FOR_DEV"]
    
    # Reset global influx_client dan query_api di modul api sebelum setiap TestClient dibuat
    # Ini penting jika startup_event gagal di tes sebelumnya.
    # Perubahan di sini: app adalah argumen posisional pertama untuk TestClient
    with patch('api.influx_client', new=None), patch('api.query_api', new=None):
        with TestClient(app) as c: # app adalah argumen posisional
            yield c
    
    # Kembalikan environment variables ke kondisi semula
    if original_valid_keys is None:
        del os.environ["VALID_API_KEYS"]
    else:
        os.environ["VALID_API_KEYS"] = original_valid_keys
    
    if original_skip_check is None and "SKIP_API_KEY_CHECK_FOR_DEV" in os.environ :
        del os.environ["SKIP_API_KEY_CHECK_FOR_DEV"]
    elif original_skip_check is not None:
        os.environ["SKIP_API_KEY_CHECK_FOR_DEV"] = original_skip_check


# --- Mock Data & Helpers ---
def create_mock_influx_record(values_dict):
    record = MagicMock()
    record.values = values_dict
    return record

def create_mock_influx_table(records_list):
    table = MagicMock()
    table.records = records_list
    return [table] # query_api.query mengembalikan list of tables

# --- Test untuk Autentikasi (melalui endpoint) ---

def test_endpoint_auth_missing_key(client):
    response = client.get("/devices/")
    assert response.status_code == 401 # Karena auto_error=True di APIKeyHeader
    assert "Not authenticated" in response.json()["detail"]

def test_endpoint_auth_invalid_key(client):
    response = client.get("/devices/", headers={"X-API-Key": INVALID_API_KEY})
    assert response.status_code == 401
    assert "API Key tidak valid atau hilang" in response.json()["detail"]

@patch('api.VALID_API_KEYS', new=set()) # Override VALID_API_KEYS menjadi kosong
def test_endpoint_auth_no_keys_configured(client): # client di sini adalah fixture, bukan TestClient baru
    # Karena VALID_API_KEYS di-patch di level modul api, kita perlu memastikan
    # TestClient menggunakan instance app yang 'melihat' perubahan ini.
    # Cara paling mudah adalah dengan membuat TestClient baru di dalam test ini
    # setelah VALID_API_KEYS di-patch.
    # Namun, fixture 'client' sudah melakukan ini dengan benar jika patch diterapkan sebelum app diimpor
    # atau jika app di-reload. Untuk kesederhanaan, kita akan mengandalkan fixture client
    # dan memastikan patch diterapkan pada objek yang benar.
    # Jika `api.VALID_API_KEYS` adalah target patch yang benar, fixture `client` seharusnya sudah cukup.
    # Error sebelumnya mungkin karena `client` yang di-pass ke test ini adalah instance lama.
    # Mari kita coba buat TestClient baru di sini untuk memastikan.
    with patch('api.influx_client', new=None), patch('api.query_api', new=None):
        # Perubahan di sini: app adalah argumen posisional pertama untuk TestClient
        with TestClient(app) as new_client: # app adalah argumen posisional
            response = new_client.get("/devices/", headers={"X-API-Key": TEST_API_KEY})
            assert response.status_code == 401
            assert "Layanan tidak dikonfigurasi dengan benar untuk autentikasi" in response.json()["detail"]

# --- Test untuk endpoint /devices/ ---

@patch('api.query_api') # Patch objek query_api di dalam modul api.py
def test_list_devices_success(mock_q_api, client):
    # Mock data untuk schema.tagValues (mendapatkan device_id unik)
    mock_device_ids_table = create_mock_influx_table([
        create_mock_influx_record({"_value": "dev001"}),
        create_mock_influx_record({"_value": "dev002"}),
        create_mock_influx_record({"_value": "dev003_no_loc"}),
    ])

    # Mock data untuk query lokasi per device_id
    mock_loc_dev001_table = create_mock_influx_table([
        create_mock_influx_record({"location": "Room A", "_time": datetime.now(timezone.utc)})
    ])
    mock_loc_dev002_table = create_mock_influx_table([
        create_mock_influx_record({"location": "Room B", "_time": datetime.now(timezone.utc)})
    ])
    mock_loc_dev003_table = create_mock_influx_table([]) # Tidak ada record lokasi

    # Atur side_effect untuk mock_q_api.query agar mengembalikan data yang berbeda per panggilan
    mock_q_api.query.side_effect = [
        mock_device_ids_table,    # Panggilan pertama (untuk device_id)
        mock_loc_dev001_table,    # Panggilan kedua (lokasi dev001)
        mock_loc_dev002_table,    # Panggilan ketiga (lokasi dev002)
        mock_loc_dev003_table,    # Panggilan keempat (lokasi dev003)
    ]

    response = client.get("/devices/", headers={"X-API-Key": TEST_API_KEY})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert {"device_id": "dev001", "location": "Room A"} in data
    assert {"device_id": "dev002", "location": "Room B"} in data
    assert {"device_id": "dev003_no_loc", "location": "N/A"} in data # Default untuk lokasi tidak ditemukan
    assert mock_q_api.query.call_count == 4 # 1 untuk IDs + 3 untuk lokasi

@patch('api.query_api')
def test_list_devices_influxdb_error(mock_q_api, client):
    from influxdb_client.client.exceptions import InfluxDBError
    mock_q_api.query.side_effect = InfluxDBError(response=MagicMock(status=500, reason="DB Error", data="details"))

    response = client.get("/devices/", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 500
    assert "Gagal query perangkat dari InfluxDB" in response.json()["detail"]

# --- Test untuk endpoint /data/ ---

@patch('api.query_api')
def test_get_sensor_data_success_no_aggregation(mock_q_api, client):
    mock_df = pd.DataFrame([
        {"_time": datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc), "device_id": "dev001", "temperature": 22.5, "humidity": 45.0},
        {"_time": datetime(2023, 1, 1, 10, 5, 0, tzinfo=timezone.utc), "device_id": "dev001", "temperature": 22.6, "humidity": 45.1},
    ])
    mock_q_api.query_data_frame.return_value = mock_df

    response = client.get(
        "/data/?device_ids=dev001&fields=temperature&fields=humidity", 
        headers={"X-API-Key": TEST_API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Perhatikan bahwa Pandas NaT/NaN akan menjadi None, dan datetime menjadi string ISO
    assert data[0]["temperature"] == 22.5
    assert data[0]["_time"] == "2023-01-01T10:00:00Z" # FastAPI akan format ke ISO string
    mock_q_api.query_data_frame.assert_called_once()
    called_query = mock_q_api.query_data_frame.call_args[1]['query']
    assert 'r.device_id == "dev001"' in called_query
    assert '(r._field == "temperature" or r._field == "humidity")' in called_query # Default jika fields tidak spesifik, atau dari parameter
    assert "aggregateWindow" not in called_query

@patch('api.query_api')
def test_get_sensor_data_success_with_aggregation(mock_q_api, client):
    mock_aggregated_df = pd.DataFrame([
        {"_time": datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc), "device_id": "dev001", "temperature_mean": 22.55},
    ])
    # Nama kolom setelah pivot dan agregasi mungkin perlu disesuaikan berdasarkan implementasi pivot Anda
    # Untuk contoh ini, kita asumsikan pivot menghasilkan kolom seperti 'temperature_mean' jika fn='mean'
    mock_q_api.query_data_frame.return_value = mock_aggregated_df

    response = client.get(
        "/data/?device_ids=dev001&fields=temperature&aggregate_window=1h&aggregate_function=mean",
        headers={"X-API-Key": TEST_API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["temperature_mean"] == 22.55 # Sesuaikan dengan output pivot Anda
    
    called_query = mock_q_api.query_data_frame.call_args[1]['query']
    assert 'aggregateWindow(every: 1h, fn: mean, createEmpty: false)' in called_query

def test_get_sensor_data_invalid_aggregation_function(client):
    response = client.get(
        "/data/?aggregate_window=1h&aggregate_function=nonexistent_func",
        headers={"X-API-Key": TEST_API_KEY}
    )
    assert response.status_code == 400
    assert "Fungsi agregasi tidak valid: nonexistent_func" in response.json()["detail"]
    assert ", ".join(ALLOWED_AGGREGATE_FUNCTIONS) in response.json()["detail"]

def test_get_sensor_data_partial_aggregation_params(client):
    response_only_window = client.get(
        "/data/?aggregate_window=1h", headers={"X-API-Key": TEST_API_KEY}
    )
    assert response_only_window.status_code == 400
    assert "aggregate_window dan aggregate_function harus digunakan bersamaan" in response_only_window.json()["detail"]

    response_only_function = client.get(
        "/data/?aggregate_function=mean", headers={"X-API-Key": TEST_API_KEY}
    )
    assert response_only_function.status_code == 400
    assert "aggregate_window dan aggregate_function harus digunakan bersamaan" in response_only_function.json()["detail"]

@patch('api.query_api')
def test_get_sensor_data_influxdb_error(mock_q_api, client):
    from influxdb_client.client.exceptions import InfluxDBError
    mock_q_api.query_data_frame.side_effect = InfluxDBError(response=MagicMock(status=500))

    response = client.get("/data/", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 500
    assert "Gagal query data dari InfluxDB" in response.json()["detail"]

def test_get_sensor_data_limit_validation(client):
    response_low = client.get("/data/?limit=0", headers={"X-API-Key": TEST_API_KEY})
    assert response_low.status_code == 422 # Error validasi FastAPI

    response_high = client.get("/data/?limit=1001", headers={"X-API-Key": TEST_API_KEY})
    assert response_high.status_code == 422

    # Untuk test limit yang valid, kita perlu mock agar tidak error karena InfluxDB tidak terpanggil
    with patch('api.query_api') as mock_q_api_valid:
        mock_q_api_valid.query_data_frame.return_value = pd.DataFrame() # Cukup kembalikan DataFrame kosong
        response_valid = client.get("/data/?limit=50", headers={"X-API-Key": TEST_API_KEY})
        assert response_valid.status_code == 200


# --- Test untuk Startup Event ---
# Menguji startup event secara langsung dengan TestClient bisa rumit.
# Cara yang lebih umum adalah menguji efek sampingnya (misalnya, apakah query_api diset).

@patch('api.InfluxDBClient') # Patch class InfluxDBClient di modul api
def test_startup_influx_ping_fails(MockInfluxDBClient, client):
    # Atur mock instance dan method ping nya
    mock_influx_instance = MockInfluxDBClient.return_value
    mock_influx_instance.ping.return_value = False # Simulasi ping gagal

    # Kita perlu membuat TestClient baru di sini agar startup_event dijalankan dengan mock ini
    # Juga, reset global influx_client dan query_api di modul api
    with patch('api.influx_client', new=None), patch('api.query_api', new=None):
        # Perubahan di sini: app adalah argumen posisional pertama untuk TestClient
        with TestClient(app) as new_client: # app adalah argumen posisional
            # Coba akses endpoint yang bergantung pada query_api
            response = new_client.get("/devices/", headers={"X-API-Key": TEST_API_KEY})
            # Jika ping gagal saat startup, query_api akan None, dan get_query_api() akan raise HTTPException 503
            assert response.status_code == 503
            assert "Koneksi ke InfluxDB belum siap atau gagal" in response.json()["detail"]
    
    MockInfluxDBClient.assert_called_once() # Pastikan client diinisialisasi
    mock_influx_instance.ping.assert_called_once() # Pastikan ping dipanggil

@patch('api.InfluxDBClient')
def test_startup_influx_connection_exception(MockInfluxDBClient, client):
    MockInfluxDBClient.side_effect = Exception("Koneksi ditolak") # Simulasi exception saat koneksi

    with patch('api.influx_client', new=None), patch('api.query_api', new=None):
        # Perubahan di sini: app adalah argumen posisional pertama untuk TestClient
        with TestClient(app) as new_client: # app adalah argumen posisional
            response = new_client.get("/devices/", headers={"X-API-Key": TEST_API_KEY})
            assert response.status_code == 503
            assert "Koneksi ke InfluxDB belum siap atau gagal" in response.json()["detail"]
    MockInfluxDBClient.assert_called_once()

# Untuk menjalankan test:
# 1. Pastikan Anda berada di direktori root proyek Anda (digitalTwin).
# 2. Jalankan: poetry run pytest
# Atau jika pytest ada di PATH: pytest
