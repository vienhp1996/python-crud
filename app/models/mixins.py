from sqlalchemy import Column, BigInteger, String, text, event
from sqlalchemy.orm import declarative_base
from app.utils.context import current_user_id_ctx

Base = declarative_base()


class AuditMixin:
    # Sử dụng BigInteger để lưu Unix timestamp
    created_at = Column(
        BigInteger,
        nullable=False,
        server_default=text("CAST(EXTRACT(EPOCH FROM now()) AS BIGINT)")
    )
    updated_at = Column(
        BigInteger,
        nullable=False,
        server_default=text("CAST(EXTRACT(EPOCH FROM now()) AS BIGINT)"),
        onupdate=text("CAST(EXTRACT(EPOCH FROM now()) AS BIGINT)")
    )
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)


# Event listener cho insert: gán created_by và updated_by
@event.listens_for(AuditMixin, "before_insert", propagate=True)
def set_created_by(mapper, connection, target):
    user_id = current_user_id_ctx.get()
    if user_id is not None:
        target.created_by = str(user_id)
        target.updated_by = str(user_id)


# Event listener cho update: chỉ cập nhật updated_by
@event.listens_for(AuditMixin, "before_update", propagate=True)
def set_updated_by(mapper, connection, target):
    user_id = current_user_id_ctx.get()
    if user_id is not None:
        target.updated_by = str(user_id)
