from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt, validator

validate_name = "Имя проекта не может быть пустым!"


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, )
    full_amount: Optional[PositiveInt] = Field(None)

    class Config:
        extra = Extra.forbid
        min_anystr_length = 1


class CharityProjectCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(...)
    full_amount: PositiveInt = Field(..., )

    class Config:
        min_anystr_length = 1


class CharityProjectUpdate(CharityProjectBase):
    @validator('name')
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError(validate_name)
        return value

    pass


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int = Field(0, )
    fully_invested: bool = Field(False, )
    create_date: datetime
    close_date: Optional[datetime] = Field(None, )

    class Config:
        orm_mode = True
