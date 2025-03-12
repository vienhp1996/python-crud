import time
from sqlalchemy import Column, BigInteger, String, text
from sqlalchemy.orm import declarative_base

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
