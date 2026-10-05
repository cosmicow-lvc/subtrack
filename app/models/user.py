from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
	from app.models.sub import Sub


class User(TimestampMixin, Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	name: Mapped[str] = mapped_column(String(100))
	hashed_password: Mapped[str] = mapped_column(String(255))
	role: Mapped[str] = mapped_column(String(30), default="user")
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)

	subscriptions: Mapped[list["Sub"]] = relationship(back_populates="user")
