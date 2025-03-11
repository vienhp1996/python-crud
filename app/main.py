from typing import Union

from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_session
from app.api.routes import user, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
