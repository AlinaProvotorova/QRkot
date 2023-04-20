from sqlalchemy import Column, Text, Integer, ForeignKey

from .base_model import BaseModel


class Donation(BaseModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text())
