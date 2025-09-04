"""
Analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.schemas.document import DocumentAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get analytics overview for the specified number of days
    """
    try:
        analytics_service = AnalyticsService(db)
        overview = await analytics_service.get_overview(days)
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics overview: {str(e)}")

@router.get("/documents")
async def get_document_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get document processing analytics
    """
    try:
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_document_analytics(start_date, end_date)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document analytics: {str(e)}")

@router.get("/processing-performance")
async def get_processing_performance(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get document processing performance metrics
    """
    try:
        analytics_service = AnalyticsService(db)
        performance = await analytics_service.get_processing_performance(days)
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting processing performance: {str(e)}")

@router.get("/ai-insights")
async def get_ai_insights(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get AI analysis insights and trends
    """
    try:
        analytics_service = AnalyticsService(db)
        insights = await analytics_service.get_ai_insights(days)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting AI insights: {str(e)}")

@router.get("/categories")
async def get_category_analytics(
    db: Session = Depends(get_db)
):
    """
    Get document category distribution
    """
    try:
        analytics_service = AnalyticsService(db)
        categories = await analytics_service.get_category_analytics()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting category analytics: {str(e)}")
