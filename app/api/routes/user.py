from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from typing import List

from app.core.database import async_session
from app.models.user import User
from app.api.schemas.user import UserCreate, UserBase, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


# Dependency lấy session DB
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


@router.get('/', response_model=List[UserResponse])
async def read_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
