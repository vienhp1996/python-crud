import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from alembic import context

# Lấy cấu hình từ file alembic.ini
config = context.config

# Cấu hình logging từ file alembic.ini nếu có
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import metadata của model
from app.models.user import Base  # Giả sử tất cả các model đều được đăng ký trong Base

target_metadata = Base.metadata


def get_url():
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline():
    """Chạy migration ở chế độ offline (không cần kết nối database)"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Chạy migration ở chế độ online với AsyncEngine"""
    connectable = create_async_engine(get_url(), poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        # Chuyển connection bất đồng bộ sang synchronous context
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
