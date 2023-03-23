from db.Base import *


class QuestionNotChek(BaseModel):
    __tablename__ = 'questions_not_check'
    question_id = Column(Integer(), ForeignKey('questions.id'))
    question = relationship('Question', backref='question_not_check', uselist=False)
