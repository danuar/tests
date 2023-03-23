from db.Base import *


class QuestionInputAnswer(BaseModel):
    __tablename__ = 'questions_input_answer'
    correct_answer = Column(String(), nullable=False)
    k_misspell = Column(Float(), nullable=False)
    question_id = Column(Integer(), ForeignKey('questions.id'))
    question = relationship('Question', backref='question_input_answer', uselist=False)

    __table_args__ = (
        CheckConstraint('k_misspell >= 0 AND k_misspell <= 1', name='misspel_check'),
    )
