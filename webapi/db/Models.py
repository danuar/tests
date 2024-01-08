from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from webapi.ViewModel import *

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now())
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())


answer_user_by_answer_test = \
    Table('answer_user_by_answer_test', Base.metadata,
          Column('answer_id', UUID(as_uuid=True), ForeignKey('answers.id')),
          Column('answer_test_id', UUID(as_uuid=True), ForeignKey('answers_test.id')),
          )


class AnswerTest(BaseModel):
    __tablename__ = 'answers_test'
    text = Column(String(), nullable=False)
    correct = Column(Boolean(), nullable=False)
    question_choice_id = Column(UUID(as_uuid=True), ForeignKey("questions_choice.id"))
    question_choice = relationship("QuestionChoice", back_populates="answers_test")
    answers = relationship("Answer", secondary=answer_user_by_answer_test, back_populates="answers_test")

    def GetViewModel(self, load_question=False) -> AnswerTestViewModel:
        return AnswerTestViewModel(self.id,
                                   self.question_choice.GetViewModel() if load_question else None,
                                   self.text, self.correct,
                                   [i.GetViewModel() for i in self.answers] if 'answers' in self.__dict__ else None)

    @staticmethod
    def CreateFrom(answer: AnswerTestViewModel):
        return AnswerTest(text=answer.text, correct=answer.is_correct,
                          question_choice_id=answer.question.id if answer.question else None,
                          id=answer.id,
                          answers=[Answer.CreateFrom(i) for i in answer.answers])


class Answer(BaseModel):
    __tablename__ = 'answers'
    mark = Column(Integer(), nullable=True)
    text_answer = Column(String(), nullable=True)
    complition_time = Column(Time(), nullable=False)
    result_test_id = Column(UUID(as_uuid=True), ForeignKey('results_tests.id'))
    result_test = relationship('ResultTest')
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    question = relationship("Question", back_populates="answers")
    answers_test = relationship("AnswerTest", secondary=answer_user_by_answer_test, back_populates="answers")

    def GetViewModel(self, load_result_test=False) -> AnswerViewModel:
        return AnswerViewModel(self.id, self.text_answer, self.complition_time,
                               self.question.GetViewModel(load_test=False) if 'question' in self.__dict__ else None,
                               self.result_test.GetViewModel() if load_result_test else None,
                               [i.GetViewModel() for i in self.answers_test] if 'answers_test' in self.__dict__ else None, self.mark)

    @staticmethod
    def CreateFrom(answer: AnswerViewModel):
        return Answer(text_answer=answer.text_answer, mark=answer.mark, complition_time=answer.complition_time,
                      id=answer.id if answer.id else None,
                      question_id=answer.question.id,
                      result_test_id=answer.result_test.id if answer.result_test and answer.result_test.id else None)


class ChapterTheory(BaseModel):
    __tablename__ = "chapters_theory"
    name = Column(VARCHAR(64))
    theory_id = Column(UUID(as_uuid=True), ForeignKey('theories.id'))
    theory = relationship("Theory", back_populates="chapters")
    pointers_to_answer = relationship("PointerToAnswer", back_populates="chapter")

    def GetViewModel(self, load_theory=True, load_pointers=False, load_user=False) -> ChapterTheoryViewModel:
        return ChapterTheoryViewModel(id_=self.id, name=self.name,
                                      theory=self.theory.GetViewModel(load_user=load_user,
                                                                      load_chapters=False) if load_theory else None,
                                      pointers=[i.GetViewModel() for i in
                                                self.pointers_to_answer] if load_pointers else None)

    @staticmethod
    def CreateFrom(chapter: ChapterTheoryViewModel):
        theory = Theory.CreateFrom(chapter.theory) if chapter.theory is not None and chapter.theory.id is None else None
        return ChapterTheory(id=chapter.id, name=chapter.name, theory=theory,
                             pointers_to_answer=[PointerToAnswer.CreateFrom(i) for i in chapter.pointers])


class PointerToAnswer(BaseModel):
    __tablename__ = 'pointers_to_answer'
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters_theory.id'))
    chapter = relationship('ChapterTheory', uselist=False, lazy=False, back_populates="pointers_to_answer")
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    question = relationship("Question", uselist=False, back_populates="pointer_to_answer")
    start = Column(Integer(), nullable=False)
    end = Column(Integer(), nullable=False)

    __table_args__ = (
        CheckConstraint('start >= 0', name='start_check'),
        CheckConstraint('"end" >= 0', name='end_check'),
    )

    def GetViewModel(self, load_question=True, load_chapter=True) -> PointerToAnswerViewModel:
        chapter = self.chapter.GetViewModel(load_pointers=False, load_theory=False) \
            if (load_chapter and 'chapter' in self.__dict__) \
            else ChapterTheoryViewModel.Get(self.chapter_id)
        return PointerToAnswerViewModel(self.id, self.start, self.end, chapter,
                                        self.question.GetViewModel() if load_question else None)

    @staticmethod
    def CreateFrom(ptr: PointerToAnswerViewModel):
        res = PointerToAnswer(id=ptr.id, start=ptr.start, end=ptr.end)
        if ptr.question is not None and ptr.question.id is None:
            res.question = Question.CreateFrom(ptr.question)
        elif ptr.question is not None:
            res.question_id = ptr.question.id
        if ptr.chapter is not None and ptr.chapter.id is None:
            res.chapter = ChapterTheory.CreateFrom(ptr.chapter)
        elif ptr.chapter is not None:
            res.chapter_id = ptr.chapter.id
        return res


class ResultTest(BaseModel):
    __tablename__ = 'results_tests'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship('User')
    test_id = Column(UUID(as_uuid=True), ForeignKey('tests.id'))
    test = relationship('Test', back_populates="results_tests")
    note = Column(String(), nullable=True)
    start_date = Column(DateTime(), nullable=False, default=lambda: datetime.datetime.now())
    completed_date = Column(DateTime(), nullable=True)

    answers = relationship("Answer", back_populates="result_test")

    def GetViewModel(self) -> ResultTestViewModel:
        return ResultTestViewModel(self.id, self.user.GetViewModel() if 'user' in self.__dict__ else UserViewModel.Update(self.user_id),
                                   self.test.GetViewModel(load_user=False, load_theory=True, load_questions=True) if 'test' in self.__dict__ else None,
                                   [i.GetViewModel() for i in self.answers] if 'answers' in self.__dict__ else None,
                                   self.start_date, self.completed_date, self.note)

    @staticmethod
    def CreateFrom(rt: ResultTestViewModel):
        return ResultTest(id=rt.id, user_id=rt.user.id, test_id=rt.test.id,
                          note=rt.note, start_date=rt.start_date,
                          completed_date=rt.completed_date, answers=[Answer.CreateFrom(i) for i in rt.answers])


class Test(BaseModel):
    __tablename__ = 'tests'
    completion_time = Column(Time(), nullable=True)
    name = Column(String(), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    creator = relationship("User", back_populates="tests")
    count_attempts = Column(Integer(), nullable=True)
    theory_id = Column(UUID(as_uuid=True), ForeignKey('theories.id'))
    theory = relationship('Theory', back_populates="tests")
    shuffle = Column(Boolean(), nullable=False)
    show_answer = Column(Boolean(), nullable=False)
    questions = relationship("Question", back_populates="test")
    results_tests = relationship("ResultTest", back_populates="test")

    __table_args__ = (
        CheckConstraint('count_attempts > 0', name='attempts_check'),
    )

    def GetViewModel(self, load_user=True, load_theory=True, load_questions=True) -> TestViewModel:
        return TestViewModel(self.id, self.completion_time, self.name, self.count_attempts,
                             self.creator.GetViewModel() if load_user else None,
                             self.theory.GetViewModel(load_user=load_user) if load_theory and 'theory' in self.__dict__ else TheoryViewModel.GetFromId(self.theory_id),
                             self.shuffle, self.show_answer,
                             [i.GetViewModel(load_test=False) for i in self.questions] if load_questions and 'questions' in self.__dict__ else None)

    @staticmethod
    def CreateFrom(test: TestViewModel):
        return Test(id=test.id, name=test.name, completion_time=test.complition_time, count_attempts=test.count_attempts,
                    creator_id=test.user.id,
                    theory=Theory.CreateFrom(test.theory) if test.theory.id is None else None,
                    shuffle=test.shuffle, show_answer=test.show_answer,
                    questions=[Question.get_type_in_db(q).CreateFrom(q).question for q in test.questions])


class Theory(BaseModel):
    __tablename__ = 'theories'
    name = Column(String(), nullable=False)
    study_time = Column(Time(), nullable=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    creator = relationship("User", back_populates="theories")
    tests = relationship("Test", back_populates="theory")
    chapters = relationship("ChapterTheory", lazy=False, back_populates="theory")

    def GetViewModel(self, load_user=True, load_chapters=True) -> TheoryViewModel:
        creator = self.creator.GetViewModel() if load_user and 'creator' in self.__dict__ else None
        return TheoryViewModel(self.id, self.name, self.study_time, [],
                               [i.GetViewModel(load_theory=False) for i in self.chapters] if load_chapters else None,
                               creator=creator)

    @staticmethod
    def CreateFrom(theory: TheoryViewModel):
        return Theory(id=theory.id, name=theory.name, study_time=theory.study_time,
                      chapters=[ChapterTheory.CreateFrom(i) for i in theory.chapters],
                      creator_id=theory.creator.id)


class User(BaseModel):
    __tablename__ = 'users'
    ipAddress = Column(String(), nullable=False, unique=True)
    userAgent = Column(String(), nullable=False, unique=True)

    results_tests = relationship("ResultTest", back_populates="user")
    tests = relationship("Test", back_populates="creator")
    theories = relationship("Theory", back_populates="creator")

    def GetViewModel(self, load_test=False, load_results=False) -> UserViewModel:
        return UserViewModel(self.id, self.ipAddress, self.userAgent,
                             [i.GetViewModel(load_user=False) for i in self.tests] if load_test else [],
                             [i.GetViewModel() for i in self.results_tests] if load_results else [])

    @staticmethod
    def CreateFrom(user: UserViewModel):
        return User(id=user.id, ipAddress=user.ip_address, userAgent=user.user_agent,
                    tests=[Test.CreateFrom(i) for i in user.tests],
                    results_tests=[ResultTest.CreateFrom(i) for i in user.results_tests])


class Question(BaseModel):
    __tablename__ = 'questions'
    name = Column(String(), nullable=False)
    complition_time = Column(Time(), nullable=True)
    weight = Column(Integer(), server_default='1')
    test_id = Column(UUID(as_uuid=True), ForeignKey('tests.id'))
    test = relationship("Test", back_populates="questions")
    pointer_to_answer = relationship("PointerToAnswer", uselist=False, back_populates="question")
    answers = relationship("Answer")

    question_choice = relationship("QuestionChoice", uselist=False, back_populates="question")
    question_input_answer = relationship("QuestionInputAnswer", uselist=False, back_populates="question")
    question_not_check = relationship("QuestionNotCheck", uselist=False, back_populates="question")

    __table_args__ = (
        CheckConstraint('weight > 0', name='weight_check'),
    )

    def GetViewModel(self, load_test=True) -> QuestionViewModel:
        ptr = self.pointer_to_answer if 'pointer_to_answer' in self.__dict__ else None
        args = (self.id, self.name, self.complition_time,
                ptr.GetViewModel(load_question=False) if ptr else None,
                (self.test.GetViewModel(load_user=False,
                                        load_theory=True) if load_test and 'test' in self.__dict__ else None),
                self.weight if 'weight' in self.__dict__ else 1)
        if 'question_not_check' in self.__dict__ and self.question_not_check is not None:
            return QuestionNotCheckViewModel(*args)
        if 'question_choice' in self.__dict__ and self.question_choice is not None:
            return (QuestionChoiceViewModel(*args)
                    .AddAnswers([i.GetViewModel() for i in self.question_choice.answers_test]))
        if 'question_input_answer' in self.__dict__ and self.question_input_answer:
            return (QuestionInputAnswerViewModel(*args)
                    .SetCorrectAnswer(self.question_input_answer.correct_answer)
                    .SetKMisspell(self.question_input_answer.k_misspell))
        return QuestionViewModel(*args)

    @staticmethod
    def get_type_in_db(question: QuestionViewModel):
        return {
            isinstance(question, QuestionChoiceViewModel): QuestionChoice,
            isinstance(question, QuestionInputAnswerViewModel): QuestionInputAnswer,
            isinstance(question, QuestionNotCheckViewModel): QuestionNotCheck,
        }.get(True, Question)

    @staticmethod
    def CreateFrom(q: QuestionViewModel):
        if q.test is None:
            kwarg = {}
        elif q.test.id is None:
            kwarg = {"test": Test.CreateFrom(q.test)}
        else:
            kwarg = {"test_id": q.test.id}
        return Question(id=q.id, name=q.name, complition_time=q.complition_time, weight=q.weight,
                        pointer_to_answer=PointerToAnswer.CreateFrom(q.pointer) if q.pointer is not None else None,
                        **kwarg
                        )


class QuestionChoice(BaseModel):
    __tablename__ = 'questions_choice'
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"))
    question = relationship("Question", lazy=False, uselist=False, back_populates="question_choice")
    answers_test = relationship("AnswerTest", lazy=False, back_populates="question_choice")

    def GetViewModel(self) -> QuestionChoiceViewModel:
        return self.question.GetViewModel()

    @staticmethod
    def CreateFrom(q: QuestionChoiceViewModel):
        res = QuestionChoice(id=q.id, question=Question.CreateFrom(q),
                             answers_test=[AnswerTest.CreateFrom(i) for i in q.answers_test if i])
        res.question.question_choice = res
        return res


class QuestionInputAnswer(BaseModel):
    __tablename__ = 'questions_input_answer'
    correct_answer = Column(String(), nullable=False)
    k_misspell = Column(Float(), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    question = relationship('Question', uselist=False, back_populates="question_input_answer")

    __table_args__ = (
        CheckConstraint('k_misspell >= 0 AND k_misspell <= 1', name='misspel_check'),
    )

    def GetViewModel(self) -> QuestionViewModel:
        return self.question.GetViewModel()

    @staticmethod
    def CreateFrom(q: QuestionInputAnswerViewModel):
        res = QuestionInputAnswer(id=q.id, question=Question.CreateFrom(q), k_misspell=q.k_misspell,
                                  correct_answer=q.correct_answer)
        res.question.question_input_answer = res
        return res


class QuestionNotCheck(BaseModel):
    __tablename__ = 'questions_not_check'
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    question = relationship('Question', uselist=False, lazy=False, back_populates="question_not_check")

    def GetViewModel(self) -> QuestionNotCheckViewModel:
        return self.question.GetViewModel()

    @staticmethod
    def CreateFrom(q: QuestionNotCheckViewModel):
        res = QuestionNotCheck(id=q.id, question=Question.CreateFrom(q))
        res.question.question_not_check = res
        return res
