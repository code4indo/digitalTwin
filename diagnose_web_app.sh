#!/bin/bash

echo "=== Diagnostic Script untuk React App ==="
echo "Mengecek status aplikasi di http://10.13.0.4:3003/"
echo ""

echo "1. Testing homepage accessibility..."
curl_response=$(curl -s -o /dev/null -w "%{http_code}" http://10.13.0.4:3003/)
echo "HTTP Status Code: $curl_response"

if [ "$curl_response" = "200" ]; then
    echo "✓ Homepage dapat diakses"
else
    echo "✗ Homepage tidak dapat diakses"
    exit 1
fi

echo ""
echo "2. Testing bundle.js accessibility..."
bundle_response=$(curl -s -o /dev/null -w "%{http_code}" http://10.13.0.4:3003/bundle.js)
echo "HTTP Status Code: $bundle_response"

if [ "$bundle_response" = "200" ]; then
    echo "✓ Bundle.js dapat diakses"
else
    echo "✗ Bundle.js tidak dapat diakses"
fi

echo ""
echo "3. Checking content size..."
content_size=$(curl -s http://10.13.0.4:3003/ | wc -c)
echo "Homepage content size: $content_size bytes"

echo ""
echo "4. Checking if HTML contains React root element..."
root_check=$(curl -s http://10.13.0.4:3003/ | grep -c 'id="root"')
if [ "$root_check" -gt 0 ]; then
    echo "✓ React root element found in HTML"
else
    echo "✗ React root element NOT found in HTML"
fi

echo ""
echo "5. Testing API connectivity from localhost..."
api_response=$(curl -s -H "X-API-Key: development_key_for_testing" -w "%{http_code}" http://10.13.0.4:8002/system/health/)
echo "API response: $api_response"

echo ""
echo "6. Checking image assets..."
logo_response=$(curl -s -o /dev/null -w "%{http_code}" http://10.13.0.4:3003/img/logo_dt.png)
echo "Logo image status: $logo_response"

echo ""
echo "7. Checking container logs for errors..."
echo "Recent logs from web_react_service:"
docker logs web_react_service --tail 5 2>/dev/null || echo "Could not retrieve container logs"

echo ""
echo "8. Checking container health..."
container_status=$(docker inspect web_react_service --format '{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
echo "Container health status: $container_status"

echo ""
echo "=== Diagnostic Complete ==="
