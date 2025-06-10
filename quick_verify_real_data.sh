#!/bin/bash

# Simple verification script for real data in 3D model
echo "🔬 Quick Verification: Real Data in 3D Model"
echo "=============================================="

echo ""
echo "1️⃣ Checking API data availability..."
RESPONSE=$(curl -s -H "X-API-Key: development_key_for_testing" http://localhost:8002/stats/environmental/)

if [ $? -eq 0 ]; then
    echo "✅ API endpoint accessible"
    
    # Extract temperature and humidity using grep and cut
    TEMP=$(echo $RESPONSE | grep -o '"avg":[0-9.]*' | head -1 | cut -d':' -f2)
    HUMIDITY=$(echo $RESPONSE | grep -o '"avg":[0-9.]*' | tail -1 | cut -d':' -f2)
    
    echo "📊 Current real data from API:"
    echo "   - Temperature avg: ${TEMP}°C"
    echo "   - Humidity avg: ${HUMIDITY}%"
    
    # Calculate expected ranges for 3D model
    TEMP_MIN=$(echo "$TEMP - 3" | bc)
    TEMP_MAX=$(echo "$TEMP + 3" | bc)
    HUMIDITY_MIN=$(echo "$HUMIDITY - 8" | bc)
    HUMIDITY_MAX=$(echo "$HUMIDITY + 8" | bc)
    
    echo ""
    echo "🎯 Expected ranges in 3D model:"
    echo "   - Temperature: ${TEMP_MIN}°C to ${TEMP_MAX}°C"
    echo "   - Humidity: ${HUMIDITY_MIN}% to ${HUMIDITY_MAX}%"
    
else
    echo "❌ API endpoint not accessible"
    exit 1
fi

echo ""
echo "2️⃣ Checking React app status..."
REACT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3003)

if [ "$REACT_STATUS" = "200" ]; then
    echo "✅ React app accessible at http://localhost:3003"
else
    echo "❌ React app not accessible (HTTP $REACT_STATUS)"
fi

echo ""
echo "3️⃣ Checking code modifications..."
if grep -q "fetchRealEnvironmentalData" /home/lambda_one/project/digitalTwin/web-react/src/components/EnhancedBuildingModel.js; then
    echo "✅ Real data fetch function found in code"
else
    echo "❌ Real data fetch function not found"
fi

if grep -q "realEnvironmentalData?.temperature?.avg" /home/lambda_one/project/digitalTwin/web-react/src/components/EnhancedBuildingModel.js; then
    echo "✅ Real temperature data usage found in code"
else
    echo "❌ Real temperature data usage not found"
fi

if grep -q "realEnvironmentalData?.humidity?.avg" /home/lambda_one/project/digitalTwin/web-react/src/components/EnhancedBuildingModel.js; then
    echo "✅ Real humidity data usage found in code"
else
    echo "❌ Real humidity data usage not found"
fi

echo ""
echo "📋 MANUAL VERIFICATION STEPS:"
echo "=============================================="
echo "1. Open browser: http://localhost:3003"
echo "2. Open DevTools (F12) → Console tab"
echo "3. Look for: 'Real environmental data fetched: {...}'"
echo "4. Open DevTools → Network tab"  
echo "5. Look for request to: 'stats/environmental'"
echo "6. Click any room in 3D model"
echo "7. Check temperature/humidity values are in expected ranges above"
echo ""
echo "✅ If values are within expected ranges, real data integration is working!"
echo "⚠️  If values are outside ranges, may need further investigation"
