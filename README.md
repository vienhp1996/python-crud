# Kích hoạt môi trường ảo cho Python

. .FastAPI/bin/activate

# Chạy project

uvicorn app.main:app --reload

# migrate db

alembic revision --autogenerate -m "Tạo bảng users"
alembic upgrade head

# Link api

http://127.0.0.1:8000/docs


