import contextvars

# Biến context lưu current user id
current_user_id_ctx = contextvars.ContextVar("current_user_id", default=None)
