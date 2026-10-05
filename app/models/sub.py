from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
	from app.models.charge import Charge
	from app.models.user import User


class Sub(TimestampMixin, Base):
	__tablename__ = "subscriptions"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
	name: Mapped[str] = mapped_column(String(150))
	frequency: Mapped[str] = mapped_column(String(30))
	category: Mapped[str] = mapped_column(String(100))
	billing_date: Mapped[date] = mapped_column(Date)
	is_variable: Mapped[bool] = mapped_column(Boolean, default=False)

	user: Mapped["User"] = relationship(back_populates="subscriptions")
	charges: Mapped[list["Charge"]] = relationship(back_populates="subscription")
