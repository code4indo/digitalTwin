#!/usr/bin/env python3
"""
Script untuk menguji apakah status perangkat sudah disembunyikan dari dashboard React
"""

import requests
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

def test_react_app_access():
    """Test akses ke React dashboard"""
    print("🌐 Testing React dashboard access...")
    try:
        response = requests.get("http://localhost:3003", timeout=10)
        if response.status_code == 200:
            print("✅ React dashboard is accessible")
            return True
        else:
            print(f"❌ React dashboard returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing React dashboard: {e}")
        return False

def test_device_status_hidden():
    """Test apakah status perangkat sudah disembunyikan menggunakan Selenium"""
    print("🔍 Testing if device status sections are hidden...")
    
    # Setup Chrome options untuk headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        # Start Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:3003")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Additional wait for React to render
        time.sleep(3)
        
        # Check 1: Status Perangkat section in ClimateDigitalTwin should be hidden/commented
        device_status_sections = []
        try:
            # Look for any text containing "Status Perangkat"
            elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Status Perangkat')]")
            device_status_sections.extend(elements)
            
            # Look for HVAC/AC, Dehumidifier, Air Purifier indicators
            hvac_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'HVAC/AC')]")
            device_status_sections.extend(hvac_elements)
            
            dehumidifier_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Dehumidifier')]")
            device_status_sections.extend(dehumidifier_elements)
            
            air_purifier_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Air Purifier')]")
            device_status_sections.extend(air_purifier_elements)
            
        except NoSuchElementException:
            pass
        
        # Check 2: Perangkat Aktif section in EnvironmentalStatus should be hidden
        device_active_sections = []
        try:
            elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Perangkat Aktif')]")
            # Filter out elements that have display:none
            visible_elements = []
            for element in elements:
                style = element.get_attribute('style')
                parent_style = element.find_element(By.XPATH, '..').get_attribute('style')
                
                # Check if element or parent has display:none
                if 'display: none' not in (style or '') and 'display: none' not in (parent_style or ''):
                    visible_elements.append(element)
            
            device_active_sections = visible_elements
            
        except NoSuchElementException:
            pass
        
        # Check for progress bars (device ratio indicators)
        progress_bars = []
        try:
            # Look for progress bars or device ratio indicators
            bars = driver.find_elements(By.XPATH, "//div[contains(@style, 'width: ') and contains(@style, 'backgroundColor')]")
            # Filter progress bars that might be related to device ratio
            for bar in bars:
                style = bar.get_attribute('style')
                parent = bar.find_element(By.XPATH, '..')
                parent_style = parent.get_attribute('style')
                
                if ('display: none' not in (style or '') and 
                    'display: none' not in (parent_style or '') and
                    'height: 8px' in (style or '')):  # Device ratio progress bars have 8px height
                    progress_bars.append(bar)
                    
        except NoSuchElementException:
            pass
        
        driver.quit()
        
        # Report results
        print(f"📊 Test Results:")
        print(f"   Device Status sections found: {len(device_status_sections)}")
        print(f"   'Perangkat Aktif' sections visible: {len(device_active_sections)}")
        print(f"   Device ratio progress bars visible: {len(progress_bars)}")
        
        # Device status sections should be hidden (0 found)
        device_status_hidden = len(device_status_sections) == 0
        
        # Perangkat Aktif should be hidden (0 visible)
        perangkat_aktif_hidden = len(device_active_sections) == 0
        
        # Device ratio progress bars should be hidden (0 visible)
        progress_bars_hidden = len(progress_bars) == 0
        
        if device_status_hidden:
            print("✅ Device Status sections are properly hidden")
        else:
            print("❌ Device Status sections are still visible")
            for elem in device_status_sections:
                print(f"   Found: {elem.text[:50]}...")
        
        if perangkat_aktif_hidden:
            print("✅ 'Perangkat Aktif' section is properly hidden")
        else:
            print("❌ 'Perangkat Aktif' section is still visible")
            for elem in device_active_sections:
                print(f"   Found: {elem.text[:50]}...")
        
        if progress_bars_hidden:
            print("✅ Device ratio progress bars are properly hidden")
        else:
            print("❌ Device ratio progress bars are still visible")
        
        return device_status_hidden and perangkat_aktif_hidden and progress_bars_hidden
        
    except TimeoutException:
        print("❌ Timeout waiting for page to load")
        return False
    except Exception as e:
        print(f"❌ Error during Selenium test: {e}")
        return False

def main():
    print("=" * 70)
    print("🧪 TESTING DEVICE STATUS HIDDEN IN REACT DASHBOARD")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: React app accessibility
    react_accessible = test_react_app_access()
    print()
    
    if not react_accessible:
        print("❌ Cannot proceed with testing - React app is not accessible")
        sys.exit(1)
    
    # Test 2: Check if device status is hidden
    device_status_hidden = test_device_status_hidden()
    print()
    
    # Summary
    print("=" * 70)
    print("📋 FINAL SUMMARY")
    print("=" * 70)
    
    if react_accessible:
        print("✅ React Dashboard: Accessible")
    else:
        print("❌ React Dashboard: Not accessible")
    
    if device_status_hidden:
        print("✅ Device Status: Successfully hidden")
        print("🎉 SUCCESS: All device status sections are now hidden!")
    else:
        print("❌ Device Status: Still visible")
        print("⚠️ ATTENTION: Some device status sections are still visible")
    
    print()
    print("🌐 Dashboard URL: http://localhost:3003")
    print("💡 You can manually verify by opening the dashboard in a browser")
    
    return react_accessible and device_status_hidden

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
