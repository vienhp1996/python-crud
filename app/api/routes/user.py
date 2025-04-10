from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc
from uuid import UUID
from typing import List, Optional

from app.api.dependencies import get_current_active_superuser
from app.models.user import User
from app.api.schemas.user import UserCreate, UserUpdate, UserResponse
from app.utils.db import get_db, fetch_all, fetch_one, fetch_many

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_active_superuser)]  # Dependency được áp dụng toàn cục
)


# Lấy danh sách user (chỉ superuser mới được truy cập)
@router.get("/", response_model=List[UserResponse])
async def read_users(
        db: AsyncSession = Depends(get_db),
        id: Optional[UUID] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None
):
    filters = []
    if id is not None:
        filters.append(User.id == id)
    if email is not None:
        # Sử dụng ilike để hỗ trợ tìm kiếm không phân biệt chữ hoa chữ thường
        filters.append(User.email.ilike(f"%{email}%"))
    if full_name is not None:
        filters.append(User.full_name.ilike(f"%{full_name}%"))
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if is_superuser is not None:
        filters.append(User.is_superuser == is_superuser)

    # Ví dụ: sắp xếp theo email tăng dần (có thể bỏ qua nếu không cần)
    users = await fetch_many(db, User, filters=filters, order_by=asc(User.email))
    return users


# Lấy thông tin 1 user theo id
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await fetch_one(db, User, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Tạo user mới: hash mật khẩu trước khi lưu
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db),
):
    # Kiểm tra trùng email
    existing_user = await fetch_one(db, User, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser
    )
    # Hash mật khẩu
    user.set_password(user_in.password)

    db.add(user)
    # gọi Flush nếu cần user.id để xử lý các phần liên quan
    await db.flush()

    await db.commit()
    await db.refresh(user)
    return user


# Cập nhật thông tin user (có thể cập nhật cả password nếu có)
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: UUID,
        user_in: UserUpdate,
        db: AsyncSession = Depends(get_db),
):
    user = await fetch_one(db, User, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.is_superuser is not None:
        user.is_superuser = user_in.is_superuser

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# Xóa user
@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await fetch_one(db, User, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"detail": "User deleted successfully"}
