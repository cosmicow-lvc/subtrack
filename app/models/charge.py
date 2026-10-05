from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.sub import Sub


class Charge(TimestampMixin, Base):
    __tablename__ = "charges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sub_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    charged_at: Mapped[date] = mapped_column(Date)

    subscription: Mapped["Sub"] = relationship(back_populates="charges")