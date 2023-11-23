import uuid
import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import *

from webapi.ViewModel import *

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now())
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())


answer_user_by_answer_test = \
    Table('answer_user_by_answer_test', Base.metadata,
          Column('answer_id', UUID(), ForeignKey('answers.id')),
          Column('answer_test_id', UUID(), ForeignKey('answers_test.id')),
          )


class AnswerTest(BaseModel):
    __tablename__ = 'answers_test'
    text = Column(String(), nullable=False)
    correct = Column(Boolean(), nullable=False)
    question_choice_id = Column(UUID(), ForeignKey("questions_choice.id"))
    question_choice = relationship("QuestionChoise", backref='answers', lazy=False)
    answers = relationship("Answer", secondary=answer_user_by_answer_test, backref='answers_test')

    def GetViewModel(self) -> AnswerTestViewModel:
        return AnswerTestViewModel(self.id, self.question_choice.GetViewModel(), self.text, self.correct,
                                   [i.GetViewModel() for i in self.answers])

    @staticmethod
    def CreateFrom(answer: AnswerTestViewModel):
        return AnswerTest(text=answer.text, correct=answer.isCorrect, question_choice=answer.question, id=answer.id,
                          answers=[Answer.CreateFrom(i) for i in answer.answers])


class Answer(BaseModel):
    __tablename__ = 'answers'
    mark = Column(Integer(), nullable=True)
    text_answer = Column(String(), nullable=True)
    complition_time = Column(Time(), nullable=False)
    result_test_id = Column(UUID(), ForeignKey('results_tests.id'))
    result_test = relationship('ResultTest', backref=backref('answers', lazy=False))
    question_id = Column(UUID(), ForeignKey('questions.id'))
    question = relationship("Question", backref='answers')
    answers_test = relationship("AnswerTest", secondary=answer_user_by_answer_test)

    def GetViewModel(self) -> AnswerViewModel:
        return AnswerViewModel(self.id, self.text_answer, self.complition_time, self.question.GetViewModel(),
                               self.result_test.GetViewModel(),
                               [i.GetViewModel() for i in self.answers_test], self.mark)

    @staticmethod
    def CreateFrom(answer: AnswerViewModel):
        return Answer(text_answer=answer.answer, mark=answer.mark, complition_time=answer.complitionTime, id=answer.id,
                      question=Question.CreateFrom(answer.question),
                      result_test=ResultTest.CreateFrom(answer.resultTest),
                      answers_test=[AnswerTest.CreateFrom(i) for i in answer.answers_test])


class ChapterTheory(BaseModel):
    __tablename__ = "chapters_theory"
    name = Column(VARCHAR(64))
    theory_id = Column(UUID(), ForeignKey('theories.id'))
    theory = relationship("Theory", backref='chapters', lazy=False)
    pointers_to_answer = relationship("PointerToAnswer")

    def GetViewModel(self) -> ChapterTheoryViewModel:
        return ChapterTheoryViewModel(id=self.id, name=self.name, theory=self.theory.GetViewModel(),
                                      pointers=[i.GetViewModel() for i in self.pointers_to_answer])

    @staticmethod
    def CreateFrom(chapter: ChapterTheoryViewModel):
        return ChapterTheory(id=chapter.id, name=chapter.name, theory=Theory.CreateFrom(chapter.theory),
                             pointers_to_answer=[PointerToAnswer.CreateFrom(i) for i in chapter.pointers])


class PointerToAnswer(BaseModel):
    __tablename__ = 'pointers_to_answer'
    chapter_id = Column(UUID(), ForeignKey('chapters_theory.id'))
    chapter = relationship('ChapterTheory', lazy=False)
    question_id = Column(UUID(), ForeignKey('questions.id'))
    question = relationship("Question", backref=backref("pointer_to_answer", uselist=False, lazy=False), uselist=False)
    start = Column(Integer(), nullable=False)
    end = Column(Integer(), nullable=False)

    __table_args__ = (
        CheckConstraint('start >= 0', name='start_check'),
        CheckConstraint('"end" >= 0', name='end_check'),
    )

    def GetViewModel(self) -> PointerToAnswerViewModel:
        return PointerToAnswerViewModel(self.id, self.start, self.end, self.chapter.GetViewModel(),
                                        self.question.GetViewModel())

    @staticmethod
    def CreateFrom(ptr: PointerToAnswerViewModel):
        return PointerToAnswer(id=ptr.id, chapter=ChapterTheory.CreateFrom(ptr.chapter),
                               start=ptr.start, end=ptr.end, question=Question.CreateFrom(ptr.question))


class ResultTest(BaseModel):
    __tablename__ = 'results_tests'
    user_id = Column(UUID(), ForeignKey('users.id'))
    user = relationship('User')
    test_id = Column(UUID(), ForeignKey('tests.id'))
    test = relationship('Test', backref='results_tests', lazy=False)
    note = Column(String(), nullable=True)
    start_date = Column(DateTime(), nullable=False, default=lambda: datetime.datetime.now())
    completed_date = Column(DateTime(), nullable=True)

    answers = relationship("Answer")

    def GetViewModel(self) -> ResultTestViewModel:
        return ResultTestViewModel(self.id, self.user.GetViewModel(), self.test.GetViewModel(),
                                   [i.GetViewModel() for i in self.answers])

    @staticmethod
    def CreateFrom(rt: ResultTestViewModel):
        return ResultTest(id=rt.id, user=User.CreateFrom(rt.user), test=Test.CreateFrom(rt.test),
                          note=rt.note, start_date=rt.startDate,
                          completed_date=rt.completedDate, answers=[Answer.CreateFrom(i) for i in rt.answers])


class Test(BaseModel):
    __tablename__ = 'tests'
    completion_time = Column(Time(), nullable=True)
    name = Column(String(), nullable=False)
    creator_id = Column(UUID(), ForeignKey('users.id'))
    creator = relationship("User", backref='tests')
    count_attempts = Column(Integer(), nullable=True)
    theory_id = Column(UUID(), ForeignKey('theories.id'))
    theory = relationship('Theory', backref='test')
    shuffle = Column(Boolean(), nullable=False)
    show_answer = Column(Boolean(), nullable=False)
    questions = relationship("Question", lazy=False)  # Todo add questions in view model

    __table_args__ = (
        CheckConstraint('count_attempts > 0', name='attempts_check'),
    )

    def GetViewModel(self) -> TestViewModel:
        return TestViewModel(self.id, self.completion_time, self.name, self.count_attempts, self.user.GetViewModel(),
                             self.theory.GetViewModel(), self.shuffle, self.show_answer)

    @staticmethod
    def CreateFrom(test: TestViewModel):
        return Test(id=test.id, name=test.name, completion_time=test.complitionTime, count_attempts=test.countAttempts,
                    creator=User.CreateFrom(test.user), theory=Theory.CreateFrom(test.theory), shuffle=test.shuffle,
                    show_answer=test.showAnswer)


class Theory(BaseModel):
    __tablename__ = 'theories'
    name = Column(String(), nullable=False)
    study_time = Column(Time(), nullable=True)
    tests = relationship("Test")
    chapters = relationship("ChapterTheory", lazy=False)

    def GetViewModel(self) -> TheoryViewModel:
        return TheoryViewModel(self.id, self.name, self.study_time, self.test.GetViewModel(),
                               [i.GetViewModel() for i in self.chapters])

    @staticmethod
    def CreateFrom(theory: TheoryViewModel):
        return Theory(id=theory.id, name=theory.name, study_time=theory.studyTime, tests=Test.CreateFrom(theory.tests),
                      chapters=[ChapterTheory.CreateFrom(i) for i in theory.chapters])


class User(BaseModel):
    __tablename__ = 'users'
    ipAddress = Column(String(), nullable=False, unique=True)
    userAgent = Column(String(), nullable=False, unique=True)
    results_tests = relationship("ResultTest", lazy=False)
    tests = relationship("Test", lazy=False)

    def GetViewModel(self) -> UserViewModel:
        return UserViewModel(self.id, self.ipAddress, self.userAgent, [i.GetViewModel() for i in self.tests],
                             [i.GetViewModel() for i in self.results_tests])

    @staticmethod
    def CreateFrom(user: UserViewModel):
        return User(id=user.id, ipAddress=user.ipAddress, userAgent=user.userAgent,
                    tests=[Test.CreateFrom(i) for i in user.tests],
                    results_tests=[ResultTest.CreateFrom(i) for i in user.resultsTests])


class Question(BaseModel):
    __tablename__ = 'questions'
    name = Column(String(), nullable=False)
    complition_time = Column(Time(), nullable=True)
    weight = Column(Integer(), server_default='1')
    test_id = Column(UUID(), ForeignKey('tests.id'))
    test = relationship("Test", backref=backref("questions", lazy=False), lazy=False)
    pointer_to_answer = relationship("PointerToAnswer", use_list=False, lazy=False)

    __table_args__ = (
        CheckConstraint('weight > 0', name='weight_check'),
    )

    def GetViewModel(self) -> QuestionViewModel:
        return QuestionViewModel(self.id, self.name, self.complition_time,
                                 PointerToAnswer.CreateFrom(self.pointer_to_answer), self.test,
                                 self.weight)

    @staticmethod
    def CreateFrom(q: QuestionViewModel):
        return Question(id=q.id, name=q.name, complition_time=q.complitionTime,
                        pointer_to_answer=PointerToAnswer.CreateFrom(q.pointer),
                        test=Test.CreateFrom(q.test), weight=q.weight)


class QuestionChoise(BaseModel):
    __tablename__ = 'questions_choice'
    question_id = Column(UUID(), ForeignKey("questions.id"))
    question = relationship("Question", backref=backref("question_choice", uselist=False, lazy=False), uselist=False)
    answers_test = relationship("AnswerTest", lazy=False)

    def GetViewModel(self) -> QuestionChoiseViewModel:
        q: Question = self.question
        return QuestionChoiseViewModel(self.id, q.name, q.complition_time,
                                       PointerToAnswer.CreateFrom(self.pointer_to_answer), q.test, q.weight,
                                       self.answers_test)

    @staticmethod
    def CreateFrom(q: QuestionChoiseViewModel):
        return QuestionChoise(id=q.id, question=Question.CreateFrom(q),
                              answers_test=[AnswerTest.CreateFrom(i) for i in q.answers_test])


class QuestionInputAnswer(BaseModel):
    __tablename__ = 'questions_input_answer'
    correct_answer = Column(String(), nullable=False)
    k_misspell = Column(Float(), nullable=False)
    question_id = Column(UUID(), ForeignKey('questions.id'))
    question = relationship('Question',
                            backref=backref('question_input_answer', uselist=False, lazy=False), uselist=False)

    __table_args__ = (
        CheckConstraint('k_misspell >= 0 AND k_misspell <= 1', name='misspel_check'),
    )

    def GetViewModel(self) -> QuestionViewModel:
        q: Question = self.question
        return QuestionInputAnswerViewModel(self.id, q.name, q.complition_time, q.pointer_to_answer, q.test,
                                            self.correct_answer, self.k_misspell, q.weight)

    @staticmethod
    def CreateFrom(q: QuestionInputAnswerViewModel):
        return QuestionInputAnswer(id=q.id, question=Question.CreateFrom(q), k_misspell=q.k_misspell,
                                   correct_answer=q.correctAnswer)


class QuestionNotCheck(BaseModel):
    __tablename__ = 'questions_not_check'
    question_id = Column(UUID(), ForeignKey('questions.id'))
    question = relationship('Question', backref=backref('question_not_check', uselist=False, lazy=False), uselist=False)

    def GetViewModel(self) -> QuestionNotCheckViewModel:
        q: Question = self.question
        return QuestionNotCheckViewModel(self.id, q.name, q.complition_time, q.pointer_to_answer, q.test,
                                         q.weight)

    @staticmethod
    def CreateFrom(q: QuestionNotCheckViewModel):
        return QuestionNotCheck(id=q.id, question=Question.CreateFrom(q))


















