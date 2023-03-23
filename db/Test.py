from sqlalchemy import Column, Integer, Time, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from db.Base import BaseModel


class Test(BaseModel):
    __tablename__ = 'tests'
    completion_time = Column(Time(), nullable=True)
    name = Column(String(), nullable=False)
    creator_id = Column(Integer(), ForeignKey('users.id'))
    creator = relationship("User", backref='tests')
    count_attempts = Column(Integer(), nullable=True)
    theory_id = Column(Integer(), ForeignKey('theories.id'))
    theory = relationship('Theory', backref='test')

    __table_args__ = (
        CheckConstraint('count_attempts > 0', name='attempts_check'),
    )
