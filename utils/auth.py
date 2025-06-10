"""
Authentication utilities for the Digital Twin API
"""
import os
from typing import Optional
from fastapi import Header, HTTPException

def get_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Get and validate API key from request header
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        str: Valid API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    # Check if we should skip API key validation for development
    if os.getenv("SKIP_API_KEY_CHECK_FOR_DEV") == "true":
        return "dev-key"
    
    # Expected API keys (can be multiple, comma-separated)
    valid_api_keys_str = os.getenv("VALID_API_KEYS", os.getenv("API_KEY", "development_key_for_testing"))
    valid_api_keys = [key.strip() for key in valid_api_keys_str.split(",")]
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key missing. Please provide X-API-Key header."
        )
    
    if x_api_key not in valid_api_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return x_api_key
