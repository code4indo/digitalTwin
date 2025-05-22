"""
Modul Flux Queries untuk Digital Twin API
Berisi semua kueri Flux yang dibutuhkan untuk manajemen iklim mikro gedung arsip
"""

from .temperature import (
    get_temperature_stats_query,
    get_average_temperature_last_hour_query,
    get_min_temperature_last_hour_query,
    get_max_temperature_last_hour_query,
    get_temperature_stats_last_hour_query,
    get_sensor_data_query
)
from .humidity import (
    get_humidity_stats_query,
    get_average_humidity_last_hour_query,
    get_min_humidity_last_hour_query,
    get_max_humidity_last_hour_query
)
from .environmental import get_environmental_stats_query
from .data import (
    get_sensor_data_query as get_general_sensor_data_query,
    get_unique_devices_query,
    get_device_history_query
)

__all__ = [
    # Temperature queries
    'get_temperature_stats_query',
    'get_average_temperature_last_hour_query',
    'get_min_temperature_last_hour_query',
    'get_max_temperature_last_hour_query',
    'get_temperature_stats_last_hour_query',
    
    # Humidity queries
    'get_humidity_stats_query',
    'get_average_humidity_last_hour_query',
    'get_min_humidity_last_hour_query',
    'get_max_humidity_last_hour_query',
    
    # Environmental queries
    'get_environmental_stats_query',
    
    # General data queries
    'get_general_sensor_data_query',
    'get_unique_devices_query',
    'get_device_history_query',
]
