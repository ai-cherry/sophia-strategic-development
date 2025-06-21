"""Router module for file_processing_router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "file_processing_router router operational"}
