from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.locale import get_message
from app.models.user import User
from app.utils.db import get_db
from app.utils.context import current_user_id_ctx  # Import biến context

# Định nghĩa OAuth2 scheme, tokenUrl phải khớp với endpoint login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Các tham số JWT, phải giống với cấu hình dùng khi tạo token
SECRET_KEY = "your-secret-key"  # Hãy thay bằng chuỗi bí mật của bạn
ALGORITHM = "HS256"


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception

    # Lưu current user id vào context variable
    current_user_id_ctx.set(user.id)

    return user


async def get_current_active_superuser(request: Request,
                                       current_user: User = Depends(get_current_user)
                                       ) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_message("insufficient_permissions", request)
        )
    return current_user
