import asyncio
from app.core.database import engine
from app.models.user import Base  # Giả sử Base được import từ models hoặc file base

async def create_tables():
    async with engine.begin() as conn:
        # Chạy hàm tạo bảng dưới dạng synchronous bên trong run_sync
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
