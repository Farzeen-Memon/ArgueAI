from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

from ..models import DebateRound, Debate, User
from ..schemas.debate import DebateRoundCreate

class RoundService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_round(
        self, 
        debate_id: int, 
        round_data: DebateRoundCreate, 
        user_id: int
    ) -> DebateRound:
        """Create a new debate round"""
        # Verify user has access to debate
        debate_result = await self.db.execute(
            select(Debate).where(Debate.id == debate_id, Debate.user_id == user_id)
        )
        debate = debate_result.scalar_one_or_none()
        
        if not debate:
            raise ValueError("Debate not found or access denied")
        
        # Check if round number already exists
        existing_round = await self.db.execute(
            select(DebateRound).where(
                DebateRound.debate_id == debate_id,
                DebateRound.round_number == round_data.round_number
            )
        )
        if existing_round.scalar_one_or_none():
            raise ValueError(f"Round {round_data.round_number} already exists")
        
        round = DebateRound(
            debate_id=debate_id,
            round_number=round_data.round_number,
            status="active"
        )
        
        self.db.add(round)
        await self.db.commit()
        await self.db.refresh(round)
        
        return round

    async def get_round(self, round_id: int, user_id: int) -> Optional[DebateRound]:
        """Get a specific round"""
        result = await self.db.execute(
            select(DebateRound)
            .options(
                selectinload(DebateRound.debate),
                selectinload(DebateRound.messages)
            )
            .join(Debate)
            .where(DebateRound.id == round_id, Debate.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_debate_rounds(self, debate_id: int, user_id: int) -> List[DebateRound]:
        """Get all rounds for a debate"""
        result = await self.db.execute(
            select(DebateRound)
            .options(
                selectinload(DebateRound.messages),
                selectinload(DebateRound.debate)
            )
            .join(Debate)
            .where(DebateRound.debate_id == debate_id, Debate.user_id == user_id)
            .order_by(DebateRound.round_number.asc())
        )
        return list(result.scalars().all())

    async def get_current_round(self, debate_id: int, user_id: int) -> Optional[DebateRound]:
        """Get the current active round for a debate"""
        result = await self.db.execute(
            select(DebateRound)
            .options(selectinload(DebateRound.debate))
            .join(Debate)
            .where(
                DebateRound.debate_id == debate_id,
                Debate.user_id == user_id,
                DebateRound.status == "active"
            )
            .order_by(DebateRound.round_number.desc())
        )
        return result.scalar_one_or_none()

    async def get_round_by_number(
        self, 
        debate_id: int, 
        round_number: int, 
        user_id: int
    ) -> Optional[DebateRound]:
        """Get a specific round by number"""
        result = await self.db.execute(
            select(DebateRound)
            .options(selectinload(DebateRound.debate))
            .join(Debate)
            .where(
                DebateRound.debate_id == debate_id,
                DebateRound.round_number == round_number,
                Debate.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def update_round_summary(
        self, 
        round_id: int, 
        summary: str,
        user_id: int
    ) -> Optional[DebateRound]:
        """Update round summary"""
        # Verify user has access
        round_result = await self.db.execute(
            select(DebateRound)
            .join(Debate)
            .where(DebateRound.id == round_id, Debate.user_id == user_id)
        )
        round = round_result.scalar_one_or_none()
        
        if not round:
            return None
        
        # Update round
        await self.db.execute(
            update(DebateRound)
            .where(DebateRound.id == round_id)
            .values(
                summary=summary,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return await self.get_round(round_id, user_id)

    async def complete_round(self, round_id: int, user_id: int) -> Optional[DebateRound]:
        """Mark a round as completed"""
        # Verify user has access
        round_result = await self.db.execute(
            select(DebateRound)
            .join(Debate)
            .where(DebateRound.id == round_id, Debate.user_id == user_id)
        )
        round = round_result.scalar_one_or_none()
        
        if not round:
            return None
        
        # Update round
        await self.db.execute(
            update(DebateRound)
            .where(DebateRound.id == round_id)
            .values(
                status="completed",
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return await self.get_round(round_id, user_id)

    async def delete_round(self, round_id: int, user_id: int) -> bool:
        """Delete a round"""
        result = await self.db.execute(
            delete(DebateRound)
            .where(DebateRound.id.in_(
                select(DebateRound.id)
                .join(Debate)
                .where(DebateRound.id == round_id, Debate.user_id == user_id)
            ))
        )
        await self.db.commit()
        
        return result.rowcount > 0

    async def get_next_round_number(self, debate_id: int, user_id: int) -> int:
        """Get the next round number for a debate"""
        result = await self.db.execute(
            select(DebateRound)
            .join(Debate)
            .where(DebateRound.debate_id == debate_id, Debate.user_id == user_id)
            .order_by(DebateRound.round_number.desc())
        )
        last_round = result.scalar_one_or_none()
        
        return (last_round.round_number + 1) if last_round else 1

    async def has_completed_rounds(self, debate_id: int, user_id: int) -> bool:
        """Check if debate has any completed rounds"""
        result = await self.db.execute(
            select(DebateRound)
            .join(Debate)
            .where(
                DebateRound.debate_id == debate_id,
                Debate.user_id == user_id,
                DebateRound.status == "completed"
            )
        )
        
        return result.scalar_one_or_none() is not None
