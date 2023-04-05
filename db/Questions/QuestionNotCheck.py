from sqlalchemy.orm import backref

from db.Base import *


class QuestionNotCheck(BaseModel):
    __tablename__ = 'questions_not_check'
    question_id = Column(Uuid(), ForeignKey('questions.id'))
    question = relationship('Question', backref=backref('question_not_check', uselist=False, lazy=False), uselist=False)
