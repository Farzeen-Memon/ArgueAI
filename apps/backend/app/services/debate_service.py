from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime

from ..models import Debate, User, DebateStatus
from ..schemas.debate import DebateCreate, DebateUpdate

class DebateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_debate(self, debate_data: DebateCreate, user_id: int) -> Debate:
        """Create a new debate"""
        debate = Debate(
            user_id=user_id,
            topic=debate_data.topic,
            style=debate_data.style,
            rounds=debate_data.rounds,
            tone=debate_data.tone,
            agent_personalities=debate_data.agent_personalities,
            status=DebateStatus.PENDING
        )
        
        self.db.add(debate)
        await self.db.commit()
        await self.db.refresh(debate)
        
        return debate

    async def get_debate(self, debate_id: int, user_id: int) -> Optional[Debate]:
        """Get a specific debate by ID and user"""
        result = await self.db.execute(
            select(Debate)
            .options(selectinload(Debate.user))
            .where(Debate.id == debate_id, Debate.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_debates(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10,
        status: Optional[str] = None
    ) -> Tuple[List[Debate], int]:
        """Get user's debates with pagination"""
        query = select(Debate).where(Debate.user_id == user_id)
        
        if status:
            query = query.where(Debate.status == status)
        
        # Get total count
        count_query = select(Debate).where(Debate.user_id == user_id)
        if status:
            count_query = count_query.where(Debate.status == status)
        
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Get paginated results
        result = await self.db.execute(
            query
            .options(selectinload(Debate.user))
            .order_by(Debate.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        debates = result.scalars().all()
        return list(debates), total

    async def update_debate(
        self, 
        debate_id: int, 
        debate_data: DebateUpdate, 
        user_id: int
    ) -> Optional[Debate]:
        """Update a debate"""
        # Build update dict with only provided fields
        update_data = {}
        for field, value in debate_data.dict(exclude_unset=True).items():
            update_data[field] = value
        
        if not update_data:
            return await self.get_debate(debate_id, user_id)
        
        # Update the debate
        await self.db.execute(
            update(Debate)
            .where(Debate.id == debate_id, Debate.user_id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_debate(debate_id, user_id)

    async def delete_debate(self, debate_id: int, user_id: int) -> bool:
        """Delete a debate"""
        result = await self.db.execute(
            delete(Debate)
            .where(Debate.id == debate_id, Debate.user_id == user_id)
        )
        await self.db.commit()
        
        return result.rowcount > 0

    async def start_debate(self, debate_id: int, user_id: int) -> Optional[Debate]:
        """Start a debate"""
        await self.db.execute(
            update(Debate)
            .where(Debate.id == debate_id, Debate.user_id == user_id)
            .values(status=DebateStatus.ACTIVE, updated_at=datetime.utcnow())
        )
        await self.db.commit()
        
        return await self.get_debate(debate_id, user_id)

    async def stop_debate(self, debate_id: int, user_id: int) -> Optional[Debate]:
        """Stop a debate"""
        await self.db.execute(
            update(Debate)
            .where(Debate.id == debate_id, Debate.user_id == user_id)
            .values(status=DebateStatus.COMPLETED, updated_at=datetime.utcnow())
        )
        await self.db.commit()
        
        return await self.get_debate(debate_id, user_id)

    async def get_debates_by_status(self, status: DebateStatus) -> List[Debate]:
        """Get all debates by status"""
        result = await self.db.execute(
            select(Debate)
            .options(selectinload(Debate.user))
            .where(Debate.status == status)
            .order_by(Debate.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_debates_count(self) -> int:
        """Get count of active debates"""
        result = await self.db.execute(
            select(Debate).where(Debate.status == DebateStatus.ACTIVE)
        )
        return len(result.scalars().all())
