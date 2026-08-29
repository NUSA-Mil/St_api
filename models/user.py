import enum
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            create_type=False,
            values_callable=lambda x: [e.value for e in x]  # Передает 'admin' вместо 'ADMIN'
        ),
        default=UserRole.USER,
        nullable=False
    )