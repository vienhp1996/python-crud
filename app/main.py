from fastapi import FastAPI
from app.api.routes import user, auth
from app.api.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(user.router)
