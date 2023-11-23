from sqlalchemy.orm import backref

from db.Base import *


class Question(BaseModel):
    __tablename__ = 'questions'
    name = Column(String(), nullable=False)
    complition_time = Column(Time(), nullable=True)
    weight = Column(Integer(), server_default='1')
    test_id = Column(UUID(), ForeignKey('tests.id'))
    test = relationship("Test", backref=backref("questions", lazy=False), lazy=False)

    __table_args__ = (
        CheckConstraint('weight > 0', name='weight_check'),
    )
