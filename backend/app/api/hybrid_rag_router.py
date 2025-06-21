"""Router module for hybrid_rag_router."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "hybrid_rag_router router operational"}
