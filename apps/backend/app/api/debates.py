from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..core.database import get_db
from ..schemas.debate import (
    DebateCreate, DebateUpdate, Debate, DebateResponse, 
    DebatesListResponse, MessageCreate, Message, MessageResponse,
    MessagesListResponse, DebateRound, DebateRoundCreate
)
from ..services.debate_service import DebateService
from ..services.message_service import MessageService
from ..services.round_service import RoundService

router = APIRouter()

# Debate endpoints
@router.post("/", response_model=DebateResponse)
async def create_debate(
    debate_data: DebateCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create a new debate"""
    try:
        debate_service = DebateService(db)
        debate = await debate_service.create_debate(debate_data, user_id)
        return DebateResponse(
            success=True,
            message="Debate created successfully",
            data=debate
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=DebatesListResponse)
async def get_debates(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get user's debates with pagination"""
    try:
        debate_service = DebateService(db)
        debates, total = await debate_service.get_user_debates(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=status
        )
        return DebatesListResponse(
            success=True,
            message="Debates retrieved successfully",
            data=debates,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{debate_id}", response_model=DebateResponse)
async def get_debate(
    debate_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific debate"""
    try:
        debate_service = DebateService(db)
        debate = await debate_service.get_debate(debate_id, user_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        
        return DebateResponse(
            success=True,
            message="Debate retrieved successfully",
            data=debate
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{debate_id}", response_model=DebateResponse)
async def update_debate(
    debate_id: int,
    debate_data: DebateUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Update a debate"""
    try:
        debate_service = DebateService(db)
        debate = await debate_service.update_debate(debate_id, debate_data, user_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        
        return DebateResponse(
            success=True,
            message="Debate updated successfully",
            data=debate
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{debate_id}")
async def delete_debate(
    debate_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a debate"""
    try:
        debate_service = DebateService(db)
        success = await debate_service.delete_debate(debate_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Debate not found")
        
        return {"success": True, "message": "Debate deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{debate_id}/start")
async def start_debate(
    debate_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Start a debate"""
    try:
        debate_service = DebateService(db)
        debate = await debate_service.start_debate(debate_id, user_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        
        return DebateResponse(
            success=True,
            message="Debate started successfully",
            data=debate
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{debate_id}/stop")
async def stop_debate(
    debate_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Stop a debate"""
    try:
        debate_service = DebateService(db)
        debate = await debate_service.stop_debate(debate_id, user_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        
        return DebateResponse(
            success=True,
            message="Debate stopped successfully",
            data=debate
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Message endpoints
@router.get("/{debate_id}/messages", response_model=MessagesListResponse)
async def get_debate_messages(
    debate_id: int,
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a debate"""
    try:
        message_service = MessageService(db)
        messages, total = await message_service.get_debate_messages(
            debate_id=debate_id,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        return MessagesListResponse(
            success=True,
            message="Messages retrieved successfully",
            data=messages,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{debate_id}/messages", response_model=MessageResponse)
async def create_message(
    debate_id: int,
    message_data: MessageCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create a new message in a debate"""
    try:
        message_service = MessageService(db)
        message = await message_service.create_message(
            debate_id=debate_id,
            message_data=message_data,
            user_id=user_id
        )
        return MessageResponse(
            success=True,
            message="Message created successfully",
            data=message
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Round endpoints
@router.get("/{debate_id}/rounds", response_model=List[DebateRound])
async def get_debate_rounds(
    debate_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get rounds for a debate"""
    try:
        round_service = RoundService(db)
        rounds = await round_service.get_debate_rounds(debate_id, user_id)
        return rounds
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{debate_id}/rounds", response_model=DebateRound)
async def create_debate_round(
    debate_id: int,
    round_data: DebateRoundCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create a new round in a debate"""
    try:
        round_service = RoundService(db)
        round = await round_service.create_round(debate_id, round_data, user_id)
        return round
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
