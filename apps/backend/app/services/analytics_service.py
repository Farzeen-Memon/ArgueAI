from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..models import Analytics, Debate, User, Message
from ..schemas.debate import AnalyticsCreate

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_analytics(self, analytics_data: AnalyticsCreate) -> Analytics:
        """Create analytics record"""
        analytics = Analytics(
            user_id=analytics_data.user_id,
            debate_id=analytics_data.debate_id,
            total_tokens=analytics_data.total_tokens,
            total_cost=analytics_data.total_cost,
            duration_seconds=analytics_data.duration_seconds,
            participant_count=analytics_data.participant_count,
            fact_check_count=analytics_data.fact_check_count
        )
        
        self.db.add(analytics)
        await self.db.commit()
        await self.db.refresh(analytics)
        
        return analytics

    async def get_user_analytics(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None
    ) -> List[Analytics]:
        """Get analytics for a user"""
        query = select(Analytics).where(Analytics.user_id == user_id)
        
        if start_date:
            query = query.where(Analytics.created_at >= start_date)
        
        result = await self.db.execute(
            query.order_by(Analytics.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_debate_analytics(
        self, 
        debate_id: int, 
        user_id: int
    ) -> Optional[Analytics]:
        """Get analytics for a specific debate"""
        result = await self.db.execute(
            select(Analytics)
            .join(Debate)
            .where(
                Analytics.debate_id == debate_id,
                Debate.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_user_summary(
        self, 
        user_id: int, 
        start_date: datetime
    ) -> Dict[str, Any]:
        """Get comprehensive analytics summary for a user"""
        
        # Total debates
        debates_result = await self.db.execute(
            select(func.count(Debate.id))
            .where(
                Debate.user_id == user_id,
                Debate.created_at >= start_date
            )
        )
        total_debates = debates_result.scalar() or 0
        
        # Completed debates
        completed_result = await self.db.execute(
            select(func.count(Debate.id))
            .where(
                Debate.user_id == user_id,
                Debate.status == 'completed',
                Debate.created_at >= start_date
            )
        )
        completed_debates = completed_result.scalar() or 0
        
        # Total tokens
        tokens_result = await self.db.execute(
            select(func.coalesce(func.sum(Message.token_count), 0))
            .join(Debate)
            .where(
                Debate.user_id == user_id,
                Message.created_at >= start_date
            )
        )
        total_tokens = tokens_result.scalar() or 0
        
        # Total cost (estimated: $0.002 per 1K tokens)
        total_cost = (total_tokens / 1000) * 0.002
        
        # Average debate duration
        duration_result = await self.db.execute(
            select(func.coalesce(func.avg(Analytics.duration_seconds), 0))
            .where(
                Analytics.user_id == user_id,
                Analytics.created_at >= start_date
            )
        )
        avg_duration = duration_result.scalar() or 0
        
        # Most active debate style
        style_result = await self.db.execute(
            select(Debate.style, func.count(Debate.id).label('count'))
            .where(
                Debate.user_id == user_id,
                Debate.created_at >= start_date
            )
            .group_by(Debate.style)
            .order_by(func.count(Debate.id).desc())
            .limit(1)
        )
        most_popular_style = style_result.first()
        
        return {
            "total_debates": total_debates,
            "completed_debates": completed_debates,
            "completion_rate": (completed_debates / total_debates * 100) if total_debates > 0 else 0,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "avg_duration_seconds": round(avg_duration, 2),
            "most_popular_style": most_popular_style[0] if most_popular_style else None,
            "period_days": (datetime.utcnow() - start_date).days
        }

    async def calculate_debate_analytics(self, debate_id: int, user_id: int) -> Dict[str, Any]:
        """Calculate analytics for a completed debate"""
        
        # Get debate details
        debate_result = await self.db.execute(
            select(Debate)
            .where(Debate.id == debate_id, Debate.user_id == user_id)
        )
        debate = debate_result.scalar_one_or_none()
        
        if not debate:
            raise ValueError("Debate not found")
        
        # Calculate duration
        duration = 0
        if debate.updated_at and debate.created_at:
            duration = int((debate.updated_at - debate.created_at).total_seconds())
        
        # Get token usage
        tokens_result = await self.db.execute(
            select(func.coalesce(func.sum(Message.token_count), 0))
            .where(Message.debate_id == debate_id)
        )
        total_tokens = tokens_result.scalar() or 0
        
        # Get fact check count
        fact_checks_result = await self.db.execute(
            select(func.count(Message.id))
            .where(
                Message.debate_id == debate_id,
                Message.message_type == 'fact_check'
            )
        )
        fact_check_count = fact_checks_result.scalar() or 0
        
        # Calculate cost (estimated)
        total_cost = (total_tokens / 1000) * 0.002
        
        # Participant count (number of unique agents)
        participants_result = await self.db.execute(
            select(func.count(func.distinct(Message.agent_id)))
            .where(Message.debate_id == debate_id)
        )
        participant_count = participants_result.scalar() or 0
        
        return {
            "user_id": user_id,
            "debate_id": debate_id,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "duration_seconds": duration,
            "fact_check_count": fact_check_count,
            "participant_count": participant_count
        }

    async def update_debate_analytics(self, debate_id: int, user_id: int):
        """Update analytics for a debate after completion"""
        try:
            analytics_data = await self.calculate_debate_analytics(debate_id, user_id)
            
            # Check if analytics already exist
            existing = await self.get_debate_analytics(debate_id, user_id)
            
            if existing:
                # Update existing record
                for field, value in analytics_data.items():
                    setattr(existing, field, value)
                await self.db.commit()
            else:
                # Create new record
                await self.create_analytics(AnalyticsCreate(**analytics_data))
                
        except Exception as e:
            print(f"Error updating debate analytics: {e}")

    async def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform-wide statistics"""
        
        # Total users
        users_result = await self.db.execute(select(func.count(User.id)))
        total_users = users_result.scalar() or 0
        
        # Total debates
        debates_result = await self.db.execute(select(func.count(Debate.id)))
        total_debates = debates_result.scalar() or 0
        
        # Active debates
        active_result = await self.db.execute(
            select(func.count(Debate.id))
            .where(Debate.status == 'active')
        )
        active_debates = active_result.scalar() or 0
        
        # Total messages
        messages_result = await self.db.execute(select(func.count(Message.id)))
        total_messages = messages_result.scalar() or 0
        
        # Total tokens
        tokens_result = await self.db.execute(
            select(func.coalesce(func.sum(Message.token_count), 0))
        )
        total_tokens = tokens_result.scalar() or 0
        
        return {
            "total_users": total_users,
            "total_debates": total_debates,
            "active_debates": active_debates,
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "estimated_total_cost": round((total_tokens / 1000) * 0.002, 2)
        }
