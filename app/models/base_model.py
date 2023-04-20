from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, CheckConstraint

from app.core.db import Base


class BaseModel(Base):
    """
    Базовый класс модели для charity_project и donation
    """
    __abstract__ = True
    __table_args__ = (
        CheckConstraint('invested_amount or 0 < full_amount > 0'),
    )

    full_amount = Column(Integer(), nullable=False)
    invested_amount = Column(Integer(), default=0, nullable=False)
    fully_invested = Column(Boolean(), default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)
