#!/usr/bin/env python3
"""
Test komprehensif untuk memastikan semua status perangkat disembunyikan
"""

import requests
import time
import sys
from datetime import datetime

def test_all_components():
    """Test semua komponen yang sudah dimodifikasi"""
    print("🔍 Testing all modified components...")
    
    components_tests = {
        'ClimateDigitalTwin.js': False,
        'EnvironmentalStatus.js': False,
        'AutomationControls.js': False,
        'EnhancedBuildingModel.js': False,
        'RoomDetails.js': False
    }
    
    # Test ClimateDigitalTwin.js
    try:
        with open('/home/lambda_one/project/digitalTwin/web-react/src/components/ClimateDigitalTwin.js', 'r') as f:
            content = f.read()
        
        if ('/* Status Perangkat disembunyikan sesuai permintaan */' in content and
            'device-status' in content and content.count('/*') >= 1):
            components_tests['ClimateDigitalTwin.js'] = True
            print("✅ ClimateDigitalTwin.js: Status perangkat properly hidden")
        else:
            print("❌ ClimateDigitalTwin.js: Status perangkat might still be visible")
            
    except Exception as e:
        print(f"❌ Error checking ClimateDigitalTwin.js: {e}")
    
    # Test EnvironmentalStatus.js
    try:
        with open('/home/lambda_one/project/digitalTwin/web-react/src/components/EnvironmentalStatus.js', 'r') as f:
            content = f.read()
        
        if ('display: \'none\'' in content and 'Perangkat Aktif' in content):
            components_tests['EnvironmentalStatus.js'] = True
            print("✅ EnvironmentalStatus.js: Perangkat Aktif properly hidden")
        else:
            print("❌ EnvironmentalStatus.js: Perangkat Aktif might still be visible")
            
    except Exception as e:
        print(f"❌ Error checking EnvironmentalStatus.js: {e}")
    
    # Test AutomationControls.js
    try:
        with open('/home/lambda_one/project/digitalTwin/web-react/src/components/AutomationControls.js', 'r') as f:
            content = f.read()
        
        if ('/* Kontrol Perangkat disembunyikan sesuai permintaan */' in content and
            'device-control' in content):
            components_tests['AutomationControls.js'] = True
            print("✅ AutomationControls.js: Kontrol Perangkat properly hidden")
        else:
            print("❌ AutomationControls.js: Kontrol Perangkat might still be visible")
            
    except Exception as e:
        print(f"❌ Error checking AutomationControls.js: {e}")
    
    # Test EnhancedBuildingModel.js
    try:
        with open('/home/lambda_one/project/digitalTwin/web-react/src/components/EnhancedBuildingModel.js', 'r') as f:
            content = f.read()
        
        if ('style={{display: \'none\'}}' in content and 'devices' in content):
            components_tests['EnhancedBuildingModel.js'] = True
            print("✅ EnhancedBuildingModel.js: Device list properly hidden")
        else:
            print("❌ EnhancedBuildingModel.js: Device list might still be visible")
            
    except Exception as e:
        print(f"❌ Error checking EnhancedBuildingModel.js: {e}")
    
    # Test RoomDetails.js
    try:
        with open('/home/lambda_one/project/digitalTwin/web-react/src/components/RoomDetails.js', 'r') as f:
            content = f.read()
        
        if ('/* Kontrol Perangkat disembunyikan sesuai permintaan */' in content and
            'devices-control' in content):
            components_tests['RoomDetails.js'] = True
            print("✅ RoomDetails.js: Kontrol Perangkat properly hidden")
        else:
            print("❌ RoomDetails.js: Kontrol Perangkat might still be visible")
            
    except Exception as e:
        print(f"❌ Error checking RoomDetails.js: {e}")
    
    return all(components_tests.values()), components_tests

def check_remaining_device_references():
    """Check jika masih ada referensi device yang belum disembunyikan"""
    print("🔍 Checking for remaining device status references...")
    
    import subprocess
    import os
    
    try:
        # Search for potential device status displays in all JS files
        result = subprocess.run([
            'grep', '-r', '-n', '-i', 
            'status.*aktif\|device.*status\|perangkat.*aktif\|status.*active',
            '/home/lambda_one/project/digitalTwin/web-react/src/components/'
        ], capture_output=True, text=True)
        
        lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Filter out commented lines and style definitions
        visible_references = []
        for line in lines:
            if line and not any(x in line.lower() for x in [
                '/*', '*/', '//', 'display: \'none\'', 'style={{display', 
                'getdevice', 'helper', 'function', 'color', 'background'
            ]):
                visible_references.append(line)
        
        if visible_references:
            print(f"⚠️ Found {len(visible_references)} potential visible device status references:")
            for ref in visible_references[:10]:  # Show first 10
                print(f"   {ref}")
            if len(visible_references) > 10:
                print(f"   ... and {len(visible_references) - 10} more")
            return False
        else:
            print("✅ No visible device status references found")
            return True
            
    except Exception as e:
        print(f"❌ Error checking references: {e}")
        return False

def main():
    print("=" * 70)
    print("🧪 COMPREHENSIVE DEVICE STATUS HIDING TEST")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Check all modified components
    all_components_hidden, component_results = test_all_components()
    print()
    
    # Test 2: Check for remaining references
    no_remaining_refs = check_remaining_device_references()
    print()
    
    # Test 3: Check dashboard accessibility
    try:
        response = requests.get("http://localhost:3003", timeout=10)
        dashboard_accessible = response.status_code == 200
        if dashboard_accessible:
            print("✅ Dashboard: Accessible")
        else:
            print(f"❌ Dashboard: Not accessible (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Dashboard: Access error - {e}")
        dashboard_accessible = False
    
    # Summary
    print("=" * 70)
    print("📋 COMPREHENSIVE SUMMARY")
    print("=" * 70)
    
    print("Component Modifications:")
    for component, hidden in component_results.items():
        status = "✅" if hidden else "❌"
        print(f"  {status} {component}")
    
    print(f"\nOverall Status:")
    if all_components_hidden:
        print("✅ All Components: Device status properly hidden")
    else:
        print("❌ Some Components: Device status might still be visible")
    
    if no_remaining_refs:
        print("✅ Code Scan: No visible device references found")
    else:
        print("⚠️ Code Scan: Some device references might still be visible")
    
    if dashboard_accessible:
        print("✅ Dashboard: Accessible")
    else:
        print("❌ Dashboard: Not accessible")
    
    overall_success = all_components_hidden and no_remaining_refs and dashboard_accessible
    
    print(f"\n{'🎉 SUCCESS' if overall_success else '⚠️ NEEDS ATTENTION'}")
    
    if overall_success:
        print("All device status sections are now completely hidden!")
    else:
        print("Some device status sections might still be visible.")
    
    print("\n🌐 Dashboard URL: http://localhost:3003")
    print("💡 Please verify manually by opening the dashboard in browser")
    
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
