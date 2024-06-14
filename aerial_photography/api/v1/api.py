from fastapi import APIRouter

from aerial_photography.api.v1.endpoints import layer
from aerial_photography.api.v1.endpoints import task

api_router = APIRouter()
api_router.include_router(layer.router, prefix="", tags=["polygon"])
api_router.include_router(task.router, prefix="", tags=["task"])

