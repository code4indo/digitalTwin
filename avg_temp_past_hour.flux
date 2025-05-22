// Flux query to calculate average temperature from all devices over the past 1 hour
// Created: May 21, 2025
// Fixed: May 21, 2025 - Fixed the missing _time column error

import "date"
import "math"

// Set time range variables
timeRangeStart = -1h
timeRangeStop = now()

// Query data from all sensor devices
from(bucket: "sensor_data_primary")
  |> range(start: timeRangeStart, stop: timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "sensor_reading")
  |> filter(fn: (r) => r["_field"] == "temperature")
  // Calculate the average temperature directly
  |> group(columns: ["location", "device_id"])
  |> mean()
  |> group()
  |> mean(column: "_value")
  |> rename(columns: {_value: "avg_temperature"})
  |> yield(name: "average_temperature_past_hour")
