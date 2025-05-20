#!/usr/bin/env python3
"""
Script to check Telegraf configuration and test HTTP data collection from BMKG.
This helps diagnose issues with data collection from the BMKG API.
"""

import requests
import json
from datetime import datetime
import os
import sys

def print_header(text):
    """Print a formatted header for better readability."""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80 + "\n")

def check_bmkg_api(url, kode_wilayah):
    """Test the BMKG API directly to ensure it's returning data."""
    print_header("TESTING BMKG API CONNECTION")
    
    full_url = f"{url}?adm4={kode_wilayah}"
    print(f"Requesting data from: {full_url}")
    
    try:
        response = requests.get(full_url, timeout=30)
        response.raise_for_status()
        
        print(f"✓ Connection successful (HTTP {response.status_code})")
        data = response.json()
        
        if "data" not in data or not data["data"]:
            print("✗ API responded but no data was found")
            return False
        
        print("✓ API returned valid JSON with data")
        
        # Check for weather forecast data structure
        if "data" in data and len(data["data"]) > 0:
            if "cuaca" in data["data"][0]:
                forecast_days = data["data"][0]["cuaca"]
                total_forecasts = sum(len(day_forecasts) for day_forecasts in forecast_days)
                print(f"✓ Found {len(forecast_days)} days with {total_forecasts} total forecast entries")
                
                # Print some sample data
                if len(forecast_days) > 0 and len(forecast_days[0]) > 0:
                    print("\nSample forecast data:")
                    sample = forecast_days[0][0]
                    for key, value in sample.items():
                        print(f"  {key}: {value}")
            else:
                print("✗ No 'cuaca' field found in data")
                return False
        else:
            print("✗ No data entries returned")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection failed: {str(e)}")
        return False
    except json.JSONDecodeError:
        print("✗ API returned invalid JSON")
        return False

def check_telegraf_config(config_file):
    """Analyze Telegraf configuration for common issues."""
    print_header("CHECKING TELEGRAF CONFIGURATION")
    
    try:
        with open(config_file, 'r') as f:
            config = f.read()
            
        # Check for BMKG HTTP input
        if "[[inputs.http]]" not in config:
            print("✗ No HTTP input plugins found in config")
            return None
            
        # Extract the URL and kode_wilayah
        bmkg_url = None
        kode_wilayah = None
        
        # Simple parsing to extract the BMKG URL
        for line in config.split('\n'):
            if "urls = [" in line and "bmkg" in line.lower():
                try:
                    bmkg_url = line.split('"')[1].split('?')[0]
                except IndexError:
                    continue
            if "kode_wilayah" in line:
                try:
                    kode_wilayah = line.strip().split('"')[-2]
                except IndexError:
                    continue
                
        if bmkg_url and kode_wilayah:
            print(f"✓ Found BMKG configuration:")
            print(f"  URL: {bmkg_url}")
            print(f"  Kode Wilayah: {kode_wilayah}")
            return {
                "url": bmkg_url,
                "kode_wilayah": kode_wilayah
            }
        else:
            print("✗ Could not find complete BMKG configuration in Telegraf config")
            return None
            
    except Exception as e:
        print(f"✗ Error reading Telegraf config: {str(e)}")
        return None

if __name__ == "__main__":
    config_file = "/home/lambda_one/project/digitalTwin/telegraf.conf"
    
    # Check Telegraf config
    bmkg_config = check_telegraf_config(config_file)
    
    if bmkg_config:
        # Test BMKG API connection
        check_bmkg_api(bmkg_config["url"], bmkg_config["kode_wilayah"])
    else:
        print("Cannot proceed with API testing due to config issues.")
