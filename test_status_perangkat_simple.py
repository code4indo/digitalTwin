#!/usr/bin/env python3
"""
Script sederhana untuk menguji apakah status perangkat sudah disembunyikan dari dashboard React
"""

import requests
import time
import sys
from datetime import datetime

def test_react_app_access():
    """Test akses ke React dashboard"""
    print("🌐 Testing React dashboard access...")
    try:
        response = requests.get("http://localhost:3003", timeout=10)
        if response.status_code == 200:
            print("✅ React dashboard is accessible")
            return True, response.text
        else:
            print(f"❌ React dashboard returned status: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Error accessing React dashboard: {e}")
        return False, None

def test_source_code_changes():
    """Test apakah perubahan kode sudah benar"""
    print("🔍 Testing source code changes...")
    
    # Check ClimateDigitalTwin.js
    try:
        with open('/home/lambda_one/project/digitalTwin/web-react/src/components/ClimateDigitalTwin.js', 'r') as f:
            climate_content = f.read()
        
        # Look for commented device status section
        device_status_commented = ('/* Status Perangkat disembunyikan sesuai permintaan */' in climate_content and
                                 '/*' in climate_content and 
                                 'device-status' in climate_content and
                                 'HVAC/AC' in climate_content)
        
        if device_status_commented:
            print("✅ ClimateDigitalTwin.js: Device status section is properly commented")
        else:
            print("❌ ClimateDigitalTwin.js: Device status section might not be properly commented")
            
    except Exception as e:
        print(f"❌ Error checking ClimateDigitalTwin.js: {e}")
        device_status_commented = False
    
    # Check EnvironmentalStatus.js
    try:
        with open('/home/lambda_one/project/digitalTwin/web-react/src/components/EnvironmentalStatus.js', 'r') as f:
            env_content = f.read()
        
        # Look for hidden health-details section
        health_details_hidden = ('display: \'none\'' in env_content and
                                'Perangkat Aktif' in env_content and
                                'health-details' in env_content)
        
        if health_details_hidden:
            print("✅ EnvironmentalStatus.js: 'Perangkat Aktif' section is properly hidden")
        else:
            print("❌ EnvironmentalStatus.js: 'Perangkat Aktif' section might not be properly hidden")
            
    except Exception as e:
        print(f"❌ Error checking EnvironmentalStatus.js: {e}")
        health_details_hidden = False
    
    return device_status_commented and health_details_hidden

def check_container_status():
    """Check if React container is running"""
    print("🐳 Checking container status...")
    try:
        import subprocess
        result = subprocess.run(['docker', 'compose', 'ps', '--format', 'json'], 
                              capture_output=True, text=True, cwd='/home/lambda_one/project/digitalTwin')
        
        if result.returncode == 0:
            import json
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    containers.append(json.loads(line))
            
            react_container = None
            for container in containers:
                if container.get('Service') == 'web-react':
                    react_container = container
                    break
            
            if react_container:
                status = react_container.get('State', 'unknown')
                health = react_container.get('Health', 'unknown')
                print(f"✅ React container status: {status} ({health})")
                return status == 'running'
            else:
                print("❌ React container not found")
                return False
        else:
            print(f"❌ Error checking container status: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking container status: {e}")
        return False

def main():
    print("=" * 70)
    print("🧪 TESTING DEVICE STATUS HIDDEN IN REACT DASHBOARD")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Container status
    container_running = check_container_status()
    print()
    
    # Test 2: Source code changes
    code_changes_correct = test_source_code_changes()
    print()
    
    # Test 3: React app accessibility
    react_accessible, html_content = test_react_app_access()
    print()
    
    # Test 4: Basic HTML content check
    html_check_passed = False
    if html_content:
        print("🔍 Checking HTML content...")
        
        # The HTML should not contain visible device status elements
        # Since React renders dynamically, we check if the basic structure is there
        if 'bundle.js' in html_content and 'Digital Twin' in html_content:
            print("✅ HTML structure looks correct")
            html_check_passed = True
        else:
            print("❌ HTML structure might be incorrect")
    
    # Summary
    print("=" * 70)
    print("📋 FINAL SUMMARY")
    print("=" * 70)
    
    if container_running:
        print("✅ React Container: Running properly")
    else:
        print("❌ React Container: Not running properly")
    
    if code_changes_correct:
        print("✅ Source Code: Device status sections properly hidden/commented")
    else:
        print("❌ Source Code: Device status sections might not be properly hidden")
    
    if react_accessible:
        print("✅ React Dashboard: Accessible")
    else:
        print("❌ React Dashboard: Not accessible")
    
    if html_check_passed:
        print("✅ HTML Content: Basic structure correct")
    else:
        print("❌ HTML Content: Issues detected")
    
    overall_success = container_running and code_changes_correct and react_accessible and html_check_passed
    
    print()
    if overall_success:
        print("🎉 SUCCESS: All checks passed!")
        print("✨ Device status sections should now be hidden in the dashboard")
    else:
        print("⚠️ ATTENTION: Some checks failed")
        print("🔧 Please review the issues above")
    
    print()
    print("🌐 Dashboard URL: http://localhost:3003")
    print("💡 You can manually verify by opening the dashboard in a browser")
    print("📝 Look for the absence of:")
    print("   - 'Status Perangkat' section with HVAC/AC, Dehumidifier, Air Purifier")
    print("   - 'Perangkat Aktif' with device ratio (e.g., '2/5 50%')")
    
    return overall_success

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
