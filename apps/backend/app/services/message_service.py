from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime

from ..models import Message, Debate, User, Agent
from ..schemas.debate import MessageCreate

class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(
        self, 
        debate_id: int, 
        message_data: MessageCreate, 
        user_id: int
    ) -> Message:
        """Create a new message"""
        # Verify user has access to debate
        debate_result = await self.db.execute(
            select(Debate).where(Debate.id == debate_id, Debate.user_id == user_id)
        )
        debate = debate_result.scalar_one_or_none()
        
        if not debate:
            raise ValueError("Debate not found or access denied")
        
        # Get or create round
        from .round_service import RoundService
        round_service = RoundService(self.db)
        current_round = await round_service.get_current_round(debate_id, user_id)
        
        if not current_round:
            # Create first round
            current_round = await round_service.create_round(
                debate_id, 
                {"round_number": 1}, 
                user_id
            )
        
        # Count tokens (simplified - in production, use actual tokenizer)
        token_count = len(message_data.content.split()) * 1.3  # Rough estimate
        
        message = Message(
            debate_id=debate_id,
            round_id=current_round.id,
            agent_id=message_data.agent_id,
            content=message_data.content,
            message_type=message_data.message_type,
            token_count=token_count
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        # Load agent relationship
        result = await self.db.execute(
            select(Message)
            .options(selectinload(Message.agent))
            .where(Message.id == message.id)
        )
        return result.scalar_one()

    async def get_message(self, message_id: int, user_id: int) -> Optional[Message]:
        """Get a specific message"""
        result = await self.db.execute(
            select(Message)
            .options(
                selectinload(Message.agent),
                selectinload(Message.debate)
            )
            .join(Debate)
            .where(Message.id == message_id, Debate.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_debate_messages(
        self, 
        debate_id: int, 
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Message], int]:
        """Get messages for a debate with pagination"""
        # Verify user has access to debate
        debate_result = await self.db.execute(
            select(Debate).where(Debate.id == debate_id, Debate.user_id == user_id)
        )
        debate = debate_result.scalar_one_or_none()
        
        if not debate:
            raise ValueError("Debate not found or access denied")
        
        # Get total count
        count_result = await self.db.execute(
            select(Message).where(Message.debate_id == debate_id)
        )
        total = len(count_result.scalars().all())
        
        # Get paginated results
        result = await self.db.execute(
            select(Message)
            .options(
                selectinload(Message.agent),
                selectinload(Message.round)
            )
            .where(Message.debate_id == debate_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        
        messages = result.scalars().all()
        return list(messages), total

    async def get_round_messages(
        self, 
        round_id: int, 
        user_id: int
    ) -> List[Message]:
        """Get messages for a specific round"""
        result = await self.db.execute(
            select(Message)
            .options(
                selectinload(Message.agent),
                selectinload(Message.round),
                selectinload(Message.debate)
            )
            .join(Debate)
            .where(Message.round_id == round_id, Debate.user_id == user_id)
            .order_by(Message.created_at.asc())
        )
        
        return list(result.scalars().all())

    async def update_message(
        self, 
        message_id: int, 
        content: str,
        user_id: int
    ) -> Optional[Message]:
        """Update a message content"""
        # Verify user has access
        message_result = await self.db.execute(
            select(Message)
            .join(Debate)
            .where(Message.id == message_id, Debate.user_id == user_id)
        )
        message = message_result.scalar_one_or_none()
        
        if not message:
            return None
        
        # Update message
        await self.db.execute(
            update(Message)
            .where(Message.id == message_id)
            .values(
                content=content,
                token_count=len(content.split()) * 1.3
            )
        )
        await self.db.commit()
        
        return await self.get_message(message_id, user_id)

    async def delete_message(self, message_id: int, user_id: int) -> bool:
        """Delete a message"""
        result = await self.db.execute(
            delete(Message)
            .where(Message.id.in_(
                select(Message.id)
                .join(Debate)
                .where(Message.id == message_id, Debate.user_id == user_id)
            ))
        )
        await self.db.commit()
        
        return result.rowcount > 0

    async def get_messages_by_agent(
        self, 
        debate_id: int, 
        agent_id: int,
        user_id: int
    ) -> List[Message]:
        """Get messages by a specific agent in a debate"""
        result = await self.db.execute(
            select(Message)
            .options(selectinload(Message.agent))
            .join(Debate)
            .where(
                Message.debate_id == debate_id,
                Message.agent_id == agent_id,
                Debate.user_id == user_id
            )
            .order_by(Message.created_at.asc())
        )
        
        return list(result.scalars().all())

    async def get_token_usage(self, debate_id: int, user_id: int) -> int:
        """Get total token usage for a debate"""
        result = await self.db.execute(
            select(Message)
            .join(Debate)
            .where(Message.debate_id == debate_id, Debate.user_id == user_id)
        )
        messages = result.scalars().all()
        
        return sum(message.token_count for message in messages)
