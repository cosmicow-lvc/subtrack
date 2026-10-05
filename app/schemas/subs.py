from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated


SubscriptionName = Annotated[
	str,
	StringConstraints(strip_whitespace=True, min_length=1, max_length=150),
]
SubscriptionFrequency = Annotated[
	str,
	StringConstraints(strip_whitespace=True, min_length=1, max_length=30),
]
SubscriptionCategory = Annotated[
	str,
	StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]


class SubCreate(BaseModel):
	name: SubscriptionName
	amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
	frequency: SubscriptionFrequency
	category: SubscriptionCategory
	billing_date: date
	is_variable: bool = False


class SubResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	user_id: int
	name: str
	amount: Decimal
	frequency: str
	category: str
	billing_date: date
	is_variable: bool
	is_active: bool
	created_at: datetime
	updated_at: datetime