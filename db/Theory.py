from sqlalchemy import Column, Time, CheckConstraint, String
from sqlalchemy.orm import relationship

from db.Base import BaseModel


class Theory(BaseModel):
    __tablename__ = 'theories'
    name = Column(String(), nullable=False)
    study_time = Column(Time(), nullable=True)
