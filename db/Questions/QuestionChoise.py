from sqlalchemy.orm import backref

from db.Base import *


class QuestionChoise(BaseModel):
    __tablename__ = 'questions_choice'
    question_id = Column(Uuid(), ForeignKey("questions.id"))
    question = relationship("Question", backref=backref("question_choice", uselist=False), uselist=False)
