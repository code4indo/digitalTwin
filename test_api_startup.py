"""
Test script to verify that the API can start up correctly
with the fixed InfluxDB service
"""
import asyncio
import logging
import sys
import time
import subprocess
import signal
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_api_startup():
    """Test that the API can start up correctly"""
    try:
        # Start the API as a subprocess
        logger.info("Starting the API...")
        api_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/home/lambda_one/project/digitalTwin"
        )
        
        # Give the API time to start up
        logger.info("Waiting for API to start...")
        time.sleep(3)
        
        # Check if the API is running
        if api_process.poll() is not None:
            # API process has terminated
            stdout, stderr = api_process.communicate()
            logger.error(f"API failed to start. Exit code: {api_process.returncode}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return False
            
        # Try to access the API
        logger.info("Testing API health endpoint...")
        try:
            response = requests.get("http://127.0.0.1:8000/health")
            if response.status_code == 200:
                logger.info(f"✅ API health endpoint returned status code {response.status_code}")
                logger.info(f"Response: {response.json()}")
                return True
            else:
                logger.error(f"❌ API health endpoint returned status code {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Failed to connect to API")
            return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        return False
    finally:
        # Make sure to terminate the API process
        try:
            if 'api_process' in locals() and api_process.poll() is None:
                logger.info("Terminating API process...")
                api_process.send_signal(signal.SIGINT)
                api_process.wait(timeout=5)
                logger.info("API process terminated")
        except Exception as e:
            logger.error(f"Failed to terminate API process: {e}")

async def main():
    """Main function"""
    success = await test_api_startup()
    
    if success:
        logger.info("API started successfully with the fixed InfluxDB service!")
        sys.exit(0)
    else:
        logger.error("Failed to start the API with the fixed InfluxDB service!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
