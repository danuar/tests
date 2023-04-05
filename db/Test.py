from sqlalchemy import Column, Integer, Time, String, ForeignKey, CheckConstraint, Uuid, Boolean
from sqlalchemy.orm import relationship

from db.Base import BaseModel


class Test(BaseModel):
    __tablename__ = 'tests'
    completion_time = Column(Time(), nullable=True)
    name = Column(String(), nullable=False)
    creator_id = Column(Uuid(), ForeignKey('users.id'))
    creator = relationship("User", backref='tests')
    count_attempts = Column(Integer(), nullable=True)
    theory_id = Column(Uuid(), ForeignKey('theories.id'))
    theory = relationship('Theory', backref='test')
    shuffle = Column(Boolean(), nullable=False)
    show_answer = Column(Boolean(), nullable=False)

    __table_args__ = (
        CheckConstraint('count_attempts > 0', name='attempts_check'),
    )
