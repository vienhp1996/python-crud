from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

# Schema dùng cho tạo user mới: thêm trường password
class UserCreate(UserBase):
    password: str

# Schema dùng cho cập nhật user: password là tùy chọn
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = None

# Schema phản hồi: không bao gồm password hoặc hashed_password
class UserResponse(UserBase):
    id: UUID

    class Config:
        orm_mode = True
