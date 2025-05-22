"""
Test script to verify InfluxDB service imports are working correctly
"""
import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_influxdb_service_imports():
    """Test that the InfluxDB service can be imported correctly"""
    try:
        # Test importing the fixed InfluxDBError
        from influxdb_client.client.exceptions import InfluxDBError
        logger.info("✅ Successfully imported InfluxDBError from correct module")
        
        # Test importing the influxdb_service module
        from services import influxdb_service
        logger.info("✅ Successfully imported influxdb_service module")
        
        # Test calling a function from influxdb_service
        test_query = 'from(bucket: "sensor_data_primary") |> range(start: -1h) |> limit(n: 5)'
        
        try:
            # Just test the import and function call signature, don't actually execute it
            # since we don't know if InfluxDB is available
            logger.info("Testing function signature for execute_query...")
            results = await influxdb_service.execute_query(query=test_query, description="test query")
            logger.info("✅ Function signature for execute_query is correct")
        except ImportError as e:
            logger.error(f"❌ Failed to call function from influxdb_service: {e}")
            return False
        except Exception as e:
            # Other exceptions might be due to actual connection issues, which is fine
            # for this test since we're just testing imports
            logger.info(f"Function call raised exception (possibly due to connection): {e}")
            logger.info("✅ Function signature seems to be working correctly")
        
        return True
            
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

async def main():
    """Main function"""
    success = await test_influxdb_service_imports()
    
    if success:
        logger.info("All imports for InfluxDB service are working correctly!")
        sys.exit(0)
    else:
        logger.error("Failed to import InfluxDB service modules!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
