from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..services.auth_service import AuthService
from ..schemas.debate import User, UserCreate

router = APIRouter()

@router.post("/register", response_model=dict)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.create_user(user_data)
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{clerk_id}", response_model=User)
async def get_user(
    clerk_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user by Clerk ID"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_clerk_id(clerk_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sync", response_model=dict)
async def sync_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Sync user from Clerk"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.sync_user(user_data)
        return {
            "success": True,
            "message": "User synced successfully",
            "user_id": user.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
