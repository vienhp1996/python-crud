from typing import Union

from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_session

app = FastAPI()

@app.get("/")
async def read_root():
    # Sử dụng session để truy vấn cơ sở dữ liệu
    async with async_session() as session:
        try:
            # Ví dụ: truy vấn đơn giản trả về chuỗi "Hello, World!"
            result = await session.execute(text("SELECT 'Hello, World!'"))
            greeting = result.scalar()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {"message": greeting}