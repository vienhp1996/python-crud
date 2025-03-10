from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Cấu hình chuỗi kết nối:
# Lưu ý: "postgresql+asyncpg" chỉ định sử dụng driver asyncpg
DATABASE_URL = "postgresql+asyncpg://vienhp:123123@localhost:5432/python"

# Tạo engine kết nối
engine = create_async_engine(DATABASE_URL, echo=True)

# Tạo session maker sử dụng AsyncSession
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
