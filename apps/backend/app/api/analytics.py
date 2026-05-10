from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..schemas.debate import Analytics, AnalyticsCreate, AnalyticsResponse
from ..services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/user/{user_id}", response_model=List[Analytics])
async def get_user_analytics(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a user"""
    try:
        analytics_service = AnalyticsService(db)
        start_date = datetime.utcnow() - timedelta(days=days)
        analytics = await analytics_service.get_user_analytics(user_id, start_date)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/debate/{debate_id}", response_model=Analytics)
async def get_debate_analytics(
    debate_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific debate"""
    try:
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_debate_analytics(debate_id, user_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Analytics not found")
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=dict)
async def create_analytics(
    analytics_data: AnalyticsCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create analytics record"""
    try:
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.create_analytics(analytics_data)
        return {
            "success": True,
            "message": "Analytics created successfully",
            "analytics_id": analytics.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary/{user_id}")
async def get_user_summary(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get user analytics summary"""
    try:
        analytics_service = AnalyticsService(db)
        start_date = datetime.utcnow() - timedelta(days=days)
        summary = await analytics_service.get_user_summary(user_id, start_date)
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
