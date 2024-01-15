#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipaddress
import random
import uuid
from abc import ABCMeta, abstractmethod
import datetime
from dataclasses import dataclass
from typing import List, Optional

from .Validator import Validator


class AbstractModelView(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def CanBeCreated(self) -> Validator:
        pass

    @abstractmethod
    def CanBeUpdated(self) -> Validator:
        if self.id is None:
            return Validator(type(self), "id", "Не заполнено id изменяемой сущности")

    def CanBeFind(self) -> Validator:
        if self.id is None:
            return Validator(type(self), "id", "Для поиска сущности необходим его id")
        return Validator.default()

    def CanBeDeleted(self) -> Validator:
        if self.id is None:
            return Validator(type(self), "id", "Для удаления сущности необходим его id")
        return Validator.default()

    @abstractmethod
    def __init__(self):
        self.id: uuid.UUID = None


class AnswerTestViewModel(AbstractModelView):
    def CanBeCreated(self) -> Validator:
        pass

    def CanBeUpdated(self) -> Validator:
        pass

    def HideAnswer(self):
        if hasattr(self, 'is_correct'):
            delattr(self, 'is_correct')
        return self

    @classmethod
    def CreateInQuestion(cls, text, is_correct):
        return AnswerTestViewModel(None, None, text, is_correct, [])

    def __init__(self, id_, question, text, is_correct, answers):
        self.id: uuid.UUID = id_
        self.question: QuestionChoiceViewModel = question
        self.text: str = text
        self.is_correct: bool = is_correct
        self.answers: List[AnswerViewModel] = answers

    @classmethod
    def FromId(cls, id_: uuid.UUID):
        return cls(id_, None, None, None, None)


class AnswerViewModel(AbstractModelView):

    @staticmethod
    def Create(complition_time: datetime.datetime, question, result_test,
               answer: str = None, mark: int = None):
        return AnswerViewModel(0, answer, complition_time, question, result_test, mark=mark)

    @staticmethod
    def Update(id_: uuid.UUID, mark: int):
        return AnswerViewModel(id_, None, None, None, None, None, mark)

    @staticmethod
    def CreateForPassintTest(text_answer: Optional[str]):
        return AnswerViewModel(0, text_answer, None, None, None)

    def CanBeCreated(self) -> Validator:
        return Validator.default()

    def AddAnswersTests(self, answers: List[AnswerTestViewModel]):
        self.answers_test.extend(answers)
        return self

    def CanBeUpdated(self) -> Validator:
        return super().CanBeUpdated()

    def __init__(self, id_: int, answer, complition_time, question, result_test, answers_test=None, mark=None):
        self.id: uuid.UUID = id_
        self.mark: int = mark
        self.text_answer: str = answer
        self.complition_time: datetime.time = complition_time
        self.question: QuestionViewModel = question
        self.result_test: ResultTestViewModel = result_test
        self.answers_test: List[AnswerTestViewModel] = answers_test if answers_test is not None else []


class ChapterTheoryViewModel(AbstractModelView):
    @staticmethod
    def Create(name: str, theory):
        return ChapterTheoryViewModel(None, name, theory, [])

    @staticmethod
    def Update(id_: int, name: str):
        return ChapterTheoryViewModel(id_, name, None, [])

    @staticmethod
    def Get(id_: int):
        return ChapterTheoryViewModel(id_, None, None, [])

    @staticmethod
    def Delete(id_: int, user_id: uuid.UUID):
        return ChapterTheoryViewModel(id_, None, TheoryViewModel.Create(None, UserViewModel.Update(user_id)), [])

    def CanBeCreated(self) -> Validator:
        return Validator(None, None, None)

    def CanBeUpdated(self) -> Validator:
        return Validator(None, None, None)

    def CanBeDeleted(self) -> Validator:
        if self.id is None or self.theory is None or self.theory.creator is None or self.theory.creator.id is None:
            return Validator(type(self), "id & creator.id", "Для удаления надо определить id главы и user_id")
        return Validator.default()

    def AddPointerToAnswer(self, pointer):
        self.pointers.append(pointer)
        return self

    def SetTheory(self, theory):
        self.theory = theory
        return self

    def SetContent(self, content):
        self.content = content
        return self

    def __init__(self, id_, name, theory, pointers):
        self.id: uuid.UUID = id_
        self.name: str = name
        self.theory: TheoryViewModel = theory
        self.pointers: List[PointerToAnswerViewModel] = pointers
        self.content = ""


class PointerToAnswerViewModel(AbstractModelView):
    @staticmethod
    def Create(aStart: int, aEnd: int):
        return PointerToAnswerViewModel(None, aStart, aEnd, None, None)

    @staticmethod
    def Delete(aId: int):
        return PointerToAnswerViewModel(aId, None, None, None, None)

    def CanBeCreated(self) -> Validator:
        pass

    def SetChapter(self, aChapter: ChapterTheoryViewModel):
        self.chapter = aChapter
        return self

    def SetQuestion(self, aQuestion):
        self.question = aQuestion
        return self

    def CanBeUpdated(self) -> Validator:
        return super().CanBeUpdated()

    def __init__(self, id_, start, end, chapter, question):
        self.id: uuid.UUID = id_
        self.start: int = start
        self.end: int = end
        self.chapter: ChapterTheoryViewModel = chapter
        self.question: QuestionViewModel = question


class QuestionViewModel(AbstractModelView):
    @classmethod
    def Create(cls, aName: str, aWeight, aComplitionTime, aTest):
        return cls(None, aName, aComplitionTime, None, aTest, aWeight)

    @staticmethod
    def Update(aId: int, aName: str, aWeight, aComplitionTime):
        return QuestionViewModel(aId, aName, aComplitionTime, None, None, aWeight)

    @staticmethod
    def Delete(aId: int):
        return QuestionViewModel(aId, None, None, None, None)

    def CanBeUpdated(self) -> Validator:
        pass

    def SetPointerToAnswer(self, aPointer: PointerToAnswerViewModel):
        self.pointer = aPointer
        return self

    def CanBeCreated(self) -> Validator:
        return Validator.default()

    def HideAnswer(self):
        return self

    def __init__(self, id_, name, complition_time, pointer, test, weight: Optional[int] = None):
        self.id: uuid.UUID = id_
        self.name: str = name
        self.complition_time: datetime.time = complition_time
        self.weight: int = weight
        self.pointer: PointerToAnswerViewModel = pointer
        self.test: TestViewModel = test
        self.type = self.__class__.__name__.replace("ViewModel", "")

    @classmethod
    def GetFromId(cls, aId):
        return QuestionViewModel(aId, None, None, None, None)


class QuestionChoiceViewModel(QuestionViewModel):
    def AddAnswers(self, aAnswers: List[AnswerTestViewModel]):
        self.answers_test.extend(aAnswers)
        return self

    def HideAnswer(self):
        super().HideAnswer()
        if hasattr(self, 'answers_test'):
            [answer.HideAnswer() for answer in self.answers_test]
        return self

    def __init__(self, id_, name, complition_time, pointer, test,
                 weight: Optional[int] = None):
        super().__init__(id_, name, complition_time, pointer, test, weight)
        self.answers_test = []


class QuestionInputAnswerViewModel(QuestionViewModel):
    def SetKMisspell(self, k: float):
        self.k_misspell = k
        return self

    def SetCorrectAnswer(self, text_answer: str):
        self.correct_answer = text_answer
        return self

    def HideAnswer(self):
        super().HideAnswer()
        if hasattr(self, 'correct_answer'):
            delattr(self, 'correct_answer')
        return self

    def __init__(self, id_, name, complition_time, pointer, test,
                 weight: Optional[float] = None, correctAnswer=None, k_misspell=1):
        super().__init__(id_, name, complition_time, pointer, test, weight)
        self.correct_answer: str = correctAnswer
        self.k_misspell: float = k_misspell


class QuestionNotCheckViewModel(QuestionViewModel):
    pass


class ResultTestViewModel(AbstractModelView):
    @staticmethod
    def Create(aUser: 'UserViewModel', aTest: 'TestViewModel', note: Optional[str] = None):
        return ResultTestViewModel(None, aUser, aTest, [], datetime.datetime.now(), None, note)

    @staticmethod
    def Update(aId: uuid.UUID, aCompletedDate: datetime.datetime, aNote: str):
        return ResultTestViewModel(aId, None, None, [], None, aCompletedDate, aNote)

    @staticmethod
    def GetById(aId: uuid.UUID):
        return ResultTestViewModel(aId, None, None, [], None, None, None)

    def setSuccess(self):
        if self.test is None or self.test.questions is None or self.answers is None:
            return False
        mark = sum(i.mark for i in self.answers if i.mark)
        all_mark = sum(i.weight for i in self.test.questions)
        if all_mark != 0:
            self.success = mark / all_mark > 0.6
        return self

    def CanBeCreated(self) -> Validator:
        pass

    def CanBeUpdated(self) -> Validator:
        pass

    def AddAnswers(self, answer: list[AnswerViewModel]):
        self.answers.extend(answer)
        return self

    def AddAnswer(self, aAnswer: AnswerViewModel):
        self.answers.append(aAnswer)
        return self

    def HideAnswer(self):
        if self.test is not None and self.test.show_answer:
            return self
        elif self.test is not None:
            self.test.HideAnswer()
        [answer.question.HideAnswer() for answer in self.answers if answer is not None and answer.question is not None]
        return self

    def __init__(self, id_: uuid.UUID, user, test, answers, startDate, completedDate: Optional[datetime.datetime],
                 note: Optional[str]):
        self.id: uuid.UUID = id_
        self.user: UserViewModel = user
        self.test: TestViewModel = test
        self.answers: List[AnswerViewModel] = answers
        self.start_date: datetime.datetime = startDate
        self.completed_date: datetime.datetime = completedDate
        self.note: str = note
        self.has_change_mark = None
        if self.test is not None and self.user is not None and self.test.user is not None:
            self.has_change_mark = self.test.user.id == self.user.id


class TestViewModel(AbstractModelView):
    @staticmethod
    def Create(aName: str, aCountAttempts: int, shuffle: bool, showAnswer: bool, user, theory,
               aComplitionTime: datetime.datetime = None):
        return TestViewModel(None, aComplitionTime, aName, aCountAttempts, user, theory, shuffle, showAnswer)

    @staticmethod
    def Update(aId: int, aName: str):
        return TestViewModel(aId, None, aName, None, None, None, None, None)

    @staticmethod
    def GetFromId(aId: uuid.UUID):
        return TestViewModel.Update(aId, None)

    def SetCreator(self, user: 'UserViewModel'):
        self.theory.creator = user  # если будет создана теория вместе с тестом
        self.user = user
        return self

    def AddQuestions(self, questions):
        self.questions.extend(questions)
        return self

    def CanBeCreated(self) -> Validator:
        return Validator.default()  # todo реализовать валидацию всех моделей

    def CanBeUpdated(self) -> Validator:
        return Validator.default()

    def HideAnswer(self, not_hide_answer_if_expire_flag_show_answer=False):
        if not (not_hide_answer_if_expire_flag_show_answer and self.show_answer):
            self.questions = [q.HideAnswer() for q in self.questions]
        return self

    def __init__(self, id_, complitionTime, name, countAttempts, user, theory, shuffle, showAnswer, questions=None):
        self.id: uuid.UUID = id_
        self.complition_time: datetime.datetime = complitionTime
        self.name: str = name
        self.count_attempts: int = countAttempts
        self.user: UserViewModel = user
        self.theory: TheoryViewModel = theory
        self.shuffle: bool = shuffle
        self.show_answer: bool = showAnswer
        self.questions: list[QuestionViewModel] = questions if questions else []


class TheoryViewModel(AbstractModelView):
    @staticmethod
    def Create(aName: str, creator, tests: List[TestViewModel] = None, aStudyTime: datetime.datetime = None,
               chapters: list[ChapterTheoryViewModel] = None):
        return TheoryViewModel(None, aName, aStudyTime, tests, [] if chapters is None else chapters, creator)

    @staticmethod
    def Update(aId: int, aName: str, aStudyTime: datetime.datetime = None):
        return TheoryViewModel(aId, aName, aStudyTime, None, [], None)

    @staticmethod
    def GetFromId(aId):
        return TheoryViewModel(aId, None, None, [], [], None)

    def CanBeCreated(self) -> Validator:
        if self.name is None or self.name == "":
            return Validator(type(self), "name", "Не заполнено имя теории")
        return Validator.default()

    def CanBeUpdated(self) -> Validator:
        super().CanBeUpdated()
        if self.creator is not None:
            return Validator(type(self), "creator", "Создатель теории не может быть изменен")
        return Validator.default()

    def SetCreator(self, creator):
        self.creator = creator
        return self

    def AddChapters(self, *chapters):
        self.chapters.extend(chapters)
        return self

    def __init__(self, id_, name, studyTime, tests, chapters, creator):
        self.id: uuid.UUID = id_
        self.name: str = name
        self.study_time: Optional[datetime.datetime] = studyTime
        self.tests: List[TestViewModel] = tests if tests is not None else []
        self.chapters: List[ChapterTheoryViewModel] = chapters
        self.creator = creator


class UserViewModel(AbstractModelView):
    @staticmethod
    def Create(aIpAddress: int, aUserAgent: str):
        return UserViewModel(None, aIpAddress, aUserAgent, [], [])

    @staticmethod
    def Update(aId: int):
        return UserViewModel(aId, None, None, [], [])

    def CanBeCreated(self) -> Validator:
        return Validator.default()

    def CanBeUpdated(self) -> Validator:
        return Validator.default()

    def CanBeFind(self) -> Validator:
        if self.id is None and self.ip_address is None and self.user_agent is None:
            return Validator(UserViewModel, "id|ipaddress|useragent",
                             "для поиска должно быть заполнено хотя бы одно поле")
        return Validator.default()

    def AddResultTest(self, aResultTest):
        self.results_tests.append(aResultTest)
        return self

    def AddTest(self, aTest: TestViewModel):
        self.tests.append(aTest)
        return self

    def SetToken(self, token: str):
        self.token = token

    def __init__(self, id_, ipAddress, userAgent, tests, resultsTests):
        self.id: uuid.UUID = id_
        self.ipaddress: int = ipAddress
        self.user_agent: str = userAgent
        self.tests: List[TestViewModel] = tests
        self.results_tests: List[ResultTestViewModel] = resultsTests
        self.token: str = ""

    @property
    def ip_address(self):
        if self.ipaddress is not None:
            return str(ipaddress.ip_address(self.ipaddress))
        return None


class StatePassingTestViewModel:

    def __init__(self, result_test: ResultTestViewModel):
        self.__result_test = result_test
        self.questions = [i for i in result_test.test.questions]
        if result_test.test.shuffle:
            random.choice(self.questions)
        self._number_current_question = 0
        self.start_datetime = datetime.datetime.now()
        self.__completed = False

    @property
    def completed(self):
        return self.__completed

    def add_answer(self, answer: AnswerViewModel):
        self._check_completed_result_test()
        answer.question = self.current_question
        answer.complition_time = self.current_complition_time
        if isinstance(answer.question, QuestionChoiceViewModel):
            answer.text_answer = None
        else:
            answer.answers_test = []
        self.__result_test.answers.append(answer)
        self.start_datetime = datetime.datetime.now()
        self.number_current_question += 1

    def complete_test(self) -> ResultTestViewModel:
        self.__completed = True
        return self.__result_test

    @property
    def current_complition_time(self):
        return (datetime.datetime.min + (datetime.datetime.now() - self.start_datetime)).time()

    @property
    def current_question(self):
        self._check_completed_result_test()
        q = self.questions[self._number_current_question].HideAnswer()
        if q.complition_time is None and q.test:
            q.complition_time = q.test.complition_time
        q.number_current_question = self.number_current_question
        return q

    @property
    def number_current_question(self):
        return self._number_current_question + 1

    @number_current_question.setter
    def number_current_question(self, value: int):
        if 0 < value <= len(self.questions):
            self._number_current_question = value - 1
        else:
            raise Exception("Установлено некорректный номер вопроса")

    def _check_completed_result_test(self):
        if self.__result_test.completed_date is not None or self.__completed:
            raise Exception("Тест уже завершен")

    def GetViewModel(self) -> dict:
        return {"answers": self.__result_test.answers,
                "current_question": self.current_question.HideAnswer(),
                "test": self.__result_test.test.HideAnswer()}


@dataclass
class ResultTestEasyViewModel:
    id: uuid.UUID
    completed_date: datetime.datetime
    name_test: str
    mark: int
    all_mark: int
    complition_time: datetime.time
    note: str
    checked: bool
