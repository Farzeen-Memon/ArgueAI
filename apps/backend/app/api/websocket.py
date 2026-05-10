from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import json
import asyncio
from ..core.database import get_db
from ..websocket.manager import ConnectionManager
from ..services.debate_service import DebateService
from ..services.message_service import MessageService
from ..schemas.debate import WebSocketMessage, AgentMessage, FactCheckUpdate

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/debate/{debate_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    debate_id: int,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time debate updates"""
    await manager.connect(websocket, debate_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message based on type
            if message_data.get("type") == "join_debate":
                await handle_join_debate(websocket, debate_id, message_data, db)
            elif message_data.get("type") == "send_message":
                await handle_send_message(websocket, debate_id, message_data, db)
            elif message_data.get("type") == "start_debate":
                await handle_start_debate(websocket, debate_id, message_data, db)
            elif message_data.get("type") == "stop_debate":
                await handle_stop_debate(websocket, debate_id, message_data, db)
            elif message_data.get("type") == "fact_check":
                await handle_fact_check(websocket, debate_id, message_data, db)
            
    except WebSocketDisconnect:
        await manager.disconnect(websocket, debate_id)

async def handle_join_debate(
    websocket: WebSocket,
    debate_id: int,
    data: Dict[str, Any],
    db: AsyncSession
):
    """Handle user joining a debate"""
    try:
        # Verify user has access to debate
        user_id = data.get("user_id")
        debate_service = DebateService(db)
        debate = await debate_service.get_debate(debate_id, user_id)
        
        if not debate:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Debate not found or access denied"
            }))
            return
        
        # Send debate state to user
        await websocket.send_text(json.dumps({
            "type": "debate_state",
            "data": {
                "debate_id": debate_id,
                "status": debate.status,
                "topic": debate.topic,
                "style": debate.style,
                "rounds": debate.rounds,
                "tone": debate.tone
            }
        }))
        
        # Notify other users
        await manager.broadcast({
            "type": "user_joined",
            "user_id": user_id,
            "debate_id": debate_id
        }, debate_id, exclude_websocket=websocket)
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def handle_send_message(
    websocket: WebSocket,
    debate_id: int,
    data: Dict[str, Any],
    db: AsyncSession
):
    """Handle sending a message"""
    try:
        user_id = data.get("user_id")
        content = data.get("content")
        agent_id = data.get("agent_id")
        message_type = data.get("message_type", "argument")
        
        message_service = MessageService(db)
        message = await message_service.create_message(
            debate_id=debate_id,
            message_data={
                "content": content,
                "message_type": message_type,
                "agent_id": agent_id
            },
            user_id=user_id
        )
        
        # Broadcast message to all connected clients
        await manager.broadcast({
            "type": "new_message",
            "data": {
                "id": message.id,
                "content": message.content,
                "message_type": message.message_type,
                "agent_id": message.agent_id,
                "agent_name": message.agent.name if message.agent else None,
                "agent_role": message.agent.role if message.agent else None,
                "created_at": message.created_at.isoformat(),
                "token_count": message.token_count
            }
        }, debate_id)
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def handle_start_debate(
    websocket: WebSocket,
    debate_id: int,
    data: Dict[str, Any],
    db: AsyncSession
):
    """Handle starting a debate"""
    try:
        user_id = data.get("user_id")
        debate_service = DebateService(db)
        debate = await debate_service.start_debate(debate_id, user_id)
        
        if debate:
            # Broadcast debate start
            await manager.broadcast({
                "type": "debate_started",
                "data": {
                    "debate_id": debate_id,
                    "status": debate.status,
                    "started_at": debate.updated_at.isoformat()
                }
            }, debate_id)
            
            # Trigger AI agent orchestration
            await trigger_ai_debate(debate_id, db)
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def handle_stop_debate(
    websocket: WebSocket,
    debate_id: int,
    data: Dict[str, Any],
    db: AsyncSession
):
    """Handle stopping a debate"""
    try:
        user_id = data.get("user_id")
        debate_service = DebateService(db)
        debate = await debate_service.stop_debate(debate_id, user_id)
        
        if debate:
            # Broadcast debate stop
            await manager.broadcast({
                "type": "debate_stopped",
                "data": {
                    "debate_id": debate_id,
                    "status": debate.status,
                    "stopped_at": debate.updated_at.isoformat()
                }
            }, debate_id)
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def handle_fact_check(
    websocket: WebSocket,
    debate_id: int,
    data: Dict[str, Any],
    db: AsyncSession
):
    """Handle fact checking a claim"""
    try:
        message_id = data.get("message_id")
        claim = data.get("claim")
        
        # Trigger fact checking in background
        asyncio.create_task(perform_fact_check(debate_id, message_id, claim, db))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def trigger_ai_debate(debate_id: int, db: AsyncSession):
    """Trigger AI agent orchestration for debate"""
    try:
        from ..agents.orchestrator import DebateOrchestrator
        
        orchestrator = DebateOrchestrator(db)
        await orchestrator.start_debate(debate_id)
        
    except Exception as e:
        print(f"Error triggering AI debate: {e}")

async def perform_fact_check(debate_id: int, message_id: int, claim: str, db: AsyncSession):
    """Perform fact checking on a claim"""
    try:
        from ..agents.fact_checker import FactCheckerAgent
        
        fact_checker = FactCheckerAgent(db)
        result = await fact_checker.check_claim(claim, message_id)
        
        # Broadcast fact check result
        await manager.broadcast({
            "type": "fact_check_result",
            "data": {
                "message_id": message_id,
                "claim": claim,
                "status": result.status,
                "confidence_score": result.confidence_score,
                "sources": result.sources,
                "reasoning": result.reasoning
            }
        }, debate_id)
        
    except Exception as e:
        print(f"Error performing fact check: {e}")
