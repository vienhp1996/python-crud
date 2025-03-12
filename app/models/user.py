import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext
from app.models.mixins import AuditMixin

Base = declarative_base()

# Cấu hình context cho việc hash mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(AuditMixin, Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=False)  # Lưu mật khẩu đã được hash

    def set_password(self, password: str):
        """Hash mật khẩu và lưu vào trường hashed_password."""
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Kiểm tra mật khẩu đầu vào có khớp với mật khẩu đã được hash hay không."""
        return pwd_context.verify(password, self.hashed_password)

    def __repr__(self):
        return f"<User(email={self.email}, full_name={self.full_name})>"
