from fastapi import APIRouter

from aerial_photography.api.v1.endpoints import layer

api_router = APIRouter()
api_router.include_router(layer.router, prefix="", tags=["polygon"])

