from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from app.core.database import async_session  # Dependency kết nối DB
from app.models.user import User
from app.api.schemas.user import UserCreate, UserResponse
from app.api.schemas.auth import Token
from app.core.locale import get_message

router = APIRouter()

# Cấu hình cho JWT
SECRET_KEY = "your-secret-key"  # Thay đổi thành một chuỗi bí mật an toàn
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Dependency lấy session DB
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Tạo JWT access token với thời gian hết hạn xác định."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=UserResponse, tags=["auth"])
async def register(user_in: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Đăng ký tài khoản mới:
    - Kiểm tra xem email đã tồn tại hay chưa.
    - Nếu đã tồn tại, trả về thông báo lỗi theo ngôn ngữ (locale).
    """
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        # Lấy thông báo lỗi từ file locale dựa theo header Accept-Language
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_message("email_already_registered", request)
        )

    # Tiếp tục quá trình tạo user...
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser
    )
    # Hash mật khẩu (ví dụ: gọi user.set_password(user_in.password))
    user.set_password(user_in.password)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token, tags=["auth"])
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    """
    Đăng nhập:
    - Sử dụng OAuth2PasswordRequestForm, trong đó `username` chính là email.
    - Xác thực mật khẩu và trả về access token nếu hợp lệ.
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message("incorrect_credentials", request),
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "id": str(user.id)},  # Chuyển user.id về chuỗi nếu là UUID
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
