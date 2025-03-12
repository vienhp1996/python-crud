from fastapi import FastAPI, HTTPException
from app.api.routes import user, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
