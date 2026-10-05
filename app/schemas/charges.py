from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ChargeCreate(BaseModel):
    sub_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    charged_at: date


class ChargeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sub_id: int
    amount: Decimal
    charged_at: date
    created_at: datetime
    updated_at: datetime