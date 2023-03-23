from db.Base import *


class QuestionChoise(BaseModel):
    __tablename__ = 'questions_choice'
    question_id = Column(Integer(), ForeignKey("questions.id"))
    question = relationship("Question", backref="question_choice", uselist=False)
