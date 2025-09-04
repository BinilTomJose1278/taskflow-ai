"""
API v1 router configuration
"""

from fastapi import APIRouter
from app.api.v1.endpoints import documents, workflows, analytics, auth, processing

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

api_router.include_router(
    workflows.router,
    prefix="/workflows",
    tags=["workflows"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

api_router.include_router(
    processing.router,
    prefix="/processing",
    tags=["processing"]
)
