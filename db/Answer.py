from db.Base import *

answer_user_by_answer_test = \
    Table('answer_user_by_answer_test', Base.metadata,
          Column('answer_id', Integer(), ForeignKey('answers.id')),
          Column('answer_test_id', Integer(), ForeignKey('answers_test.id')),
          )


class AnswerTest(BaseModel):
    __tablename__ = 'answers_test'
    text = Column(String(), nullable=False)
    correct = Column(Boolean(), nullable=False)
    question_choice_id = Column(Integer(), ForeignKey("questions_choice.id"))
    question_choice = relationship("QuestionChoice", backref='answers')
    answers = relationship("Answer", secondary=answer_user_by_answer_test, backref='answers_test')


class Answer(BaseModel):
    __tablename__ = 'answers'
    mark = Column(Integer(), nullable=True)
    text_answer = Column(Integer(), nullable=True)
    complition_time = Column(Time(), nullable=False)
    result_test_id = Column(Integer(), ForeignKey('results_tests.id'))
    result_test = relationship('ResultTest', backref='answers')
    question_id = Column(Integer(), ForeignKey('questions.id'))
    question = relationship("Question", backref='answers')

