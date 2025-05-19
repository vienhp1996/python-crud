# Đăng ký, đăng nhập

- Đăng ký: Kiểm tra xem email đã được đăng ký chưa, nếu chưa thì được đăng ký
- Đăng nhập: Kiểm tra email có trong DB chưa, nếu ko có thì báo email không tồn tai. Nếu có thì tiếp tục check Mật khẩu,
  hợp lệ thì trả về access token

# User

- Các chức năng CRUD liên quan đến User đều cần quyền quản lý và check qua get_current_active_superuser

# Task

- Tạo: các User đều có thể tạo task
- Lấy danh sách: nếu User là quản lý thì có thể xem tất cả các task dựa theo điều kiện lọc, nếu là User thường thì chỉ
  được xem Task của baản thân
- Cập nhật, xoá: cần quyền quản lý và check qua get_current_active_superuser
- Hoàn thành: chỉ có task của bản thân mới có thể hoàn thành
- Đánh giá: chỉ có thể đánh giá Task đã hoàn thành, cần quyền quản lý và check qua get_current_active_superuser

# Kích hoạt môi trường ảo cho Python

. .FastAPI/bin/activate

# Chạy project

uvicorn app.main:app --reload

# migrate db

alembic revision --autogenerate -m "Tạo bảng users"
alembic upgrade head

# Link api

http://127.0.0.1:8000/docs


