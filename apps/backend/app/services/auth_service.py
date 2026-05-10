from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from ..models import User
from ..schemas.debate import UserCreate

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = await self.get_user_by_clerk_id(user_data.clerk_id)
        if existing_user:
            raise ValueError("User already exists")
        
        user = User(
            clerk_id=user_data.clerk_id,
            email=user_data.email,
            name=user_data.name,
            avatar_url=user_data.avatar_url
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user

    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[User]:
        """Get user by Clerk ID"""
        result = await self.db.execute(
            select(User).where(User.clerk_id == clerk_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def sync_user(self, user_data: UserCreate) -> User:
        """Sync user data from Clerk (create or update)"""
        existing_user = await self.get_user_by_clerk_id(user_data.clerk_id)
        
        if existing_user:
            # Update existing user
            existing_user.email = user_data.email
            existing_user.name = user_data.name
            existing_user.avatar_url = user_data.avatar_url
            await self.db.commit()
            await self.db.refresh(existing_user)
            return existing_user
        else:
            # Create new user
            return await self.create_user(user_data)

    async def update_user(
        self, 
        user_id: int, 
        name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Optional[User]:
        """Update user profile"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        if name is not None:
            user.name = name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
