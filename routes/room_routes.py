"""
API routes untuk data ruangan dalam aplikasi Digital Twin.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, List, Any, Optional

# Import service
from services.room_service import get_room_details, get_room_list

# Import get_api_key dari api.py
from utils.auth import get_api_key

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("/", summary="Dapatkan daftar semua ruangan", 
            response_model=List[Dict[str, Any]])
async def get_rooms_endpoint(
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil daftar semua ruangan dengan informasi dasar.
    Memerlukan autentikasi API Key.
    """
    return await get_room_list()

@router.get("/{room_id}", summary="Dapatkan detail ruangan tertentu", 
            response_model=Dict[str, Any])
async def get_room_details_endpoint(
    room_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Mengambil data detail ruangan tertentu, termasuk kondisi lingkungan terkini
    dan informasi perangkat.
    
    Args:
        room_id (str): ID ruangan (contoh: F2, G3, dsb)
        
    Returns:
        Dict[str, Any]: Data ruangan dengan format JSON
    """
    room_data = await get_room_details(room_id)
    if not room_data:
        raise HTTPException(status_code=404, detail=f"Ruangan dengan ID {room_id} tidak ditemukan")
    return room_data
