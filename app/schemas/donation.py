from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = Field(None, min_length=1)


class DonationBase(DonationCreate):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDB(DonationBase):
    user_id: int
    invested_amount: int = Field(0, )
    fully_invested: bool = Field(False, )
    close_date: Optional[datetime] = Field(None, )

    class Config:
        orm_mode = True
