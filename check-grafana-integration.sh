#!/bin/bash

# Script untuk memeriksa koneksi ke Grafana dan status integrasi Digital Twin
# Usage: ./check-grafana-integration.sh [--grafana-url URL]

GRAFANA_URL=${REACT_APP_GRAFANA_URL:-"http://localhost:3000"}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --grafana-url)
      GRAFANA_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./check-grafana-integration.sh [--grafana-url URL]"
      exit 1
      ;;
  esac
done

echo "=== Checking Grafana Integration ==="

# Check if Grafana is running
echo -n "Checking Grafana service at $GRAFANA_URL: "
if curl -s --head "$GRAFANA_URL" | grep "200\|302" > /dev/null; then
  echo "✅ Grafana is running"
else
  echo "❌ Cannot connect to Grafana at $GRAFANA_URL"
  echo "Make sure Grafana is running and accessible."
  exit 1
fi

# Check if embedding is allowed
echo -n "Checking if embedding is allowed: "
HEALTH_ENDPOINT="$GRAFANA_URL/api/health"
if curl -s "$HEALTH_ENDPOINT" | grep -q "database"; then
  echo "✅ Grafana API is accessible"
else
  echo "⚠️ Cannot access Grafana API. Embedding might not work."
  echo "Please check if Grafana allows API access."
fi

# Check environment variables
echo -e "\nChecking environment variables for React app:"
ENV_ISSUES=0

if [ -f "/home/lambda_one/project/digitalTwin/web-react/.env.local" ]; then
  echo "Found .env.local file ✅"
  
  # Check specific variables
  if grep -q "REACT_APP_GRAFANA_URL" /home/lambda_one/project/digitalTwin/web-react/.env.local; then
    echo "- REACT_APP_GRAFANA_URL is defined ✅"
  else
    echo "- REACT_APP_GRAFANA_URL is missing ❌"
    ENV_ISSUES=$((ENV_ISSUES + 1))
  fi
  
  if grep -q "REACT_APP_GRAFANA_DASHBOARD_ID" /home/lambda_one/project/digitalTwin/web-react/.env.local; then
    echo "- REACT_APP_GRAFANA_DASHBOARD_ID is defined ✅"
  else
    echo "- REACT_APP_GRAFANA_DASHBOARD_ID is missing ❌"
    ENV_ISSUES=$((ENV_ISSUES + 1))
  fi
  
  if grep -q "REACT_APP_GRAFANA_PANEL_ID" /home/lambda_one/project/digitalTwin/web-react/.env.local; then
    echo "- REACT_APP_GRAFANA_PANEL_ID is defined ✅"
  else
    echo "- REACT_APP_GRAFANA_PANEL_ID is missing ❌"
    ENV_ISSUES=$((ENV_ISSUES + 1))
  fi
else
  echo "No .env.local file found ❌"
  echo "Please create .env.local file from template."
  ENV_ISSUES=$((ENV_ISSUES + 1))
fi

# Summary
echo -e "\n=== Integration Status Summary ==="
if [ $ENV_ISSUES -eq 0 ]; then
  echo "✅ All required configurations are in place."
  echo "The Grafana integration should work properly."
else
  echo "⚠️ Found $ENV_ISSUES issue(s) that might affect the Grafana integration."
  echo "Please check the issues mentioned above."
fi

echo -e "\nFor more information on how to set up the Grafana integration,"
echo "refer to the documentation at docs/grafana-integration.md"
