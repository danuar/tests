#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipaddress
import random
import uuid
from abc import ABCMeta, abstractmethod
import datetime
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
        self.id: int = None


class AnswerTestViewModel(AbstractModelView):
    def CanBeCreated(self) -> Validator:
        pass

    def CanBeUpdated(self) -> Validator:
        pass

    @classmethod
    def CreateInQuestion(cls, text, is_correct):
        return AnswerTestViewModel(None, None, text, is_correct, [])

    def __init__(self, id_, question, text, is_correct, answers):
        self.id: int = id_
        self.question: QuestionChoiceViewModel = question
        self.text: str = text
        self.isCorrect: bool = is_correct
        self.answers: List[AnswerViewModel] = answers


class AnswerViewModel(AbstractModelView):

    @staticmethod
    def Create(complition_time: datetime.datetime, question, result_test,
               answer: str = None, mark: int = None):
        return AnswerViewModel(0, answer, complition_time, question, result_test, mark=mark)

    @staticmethod
    def CreateForPassintTest(text_answer: Optional[str]):
        return AnswerViewModel(0, text_answer, None, None, None)



    def CanBeCreated(self) -> Validator:
        pass

    def AddAnswersTests(self, answers: List[AnswerTestViewModel]):
        self.answers_test.extend(answers)

    def CanBeUpdated(self) -> Validator:
        return super().CanBeUpdated()

    def __init__(self, id_: int, answer, complition_time, question, result_test, answers_test=None, mark=None):
        self.id: int = id_
        self.mark: int = mark
        self.answer: str = answer
        self.complitionTime: datetime.datetime = complition_time
        self.question: QuestionViewModel = question
        self.resultTest: ResultTestViewModel = result_test
        self.answers_test: List[AnswerTestViewModel] = answers_test


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

    def SetTheory(self, theory):
        self.theory = theory
        return self

    def SetContent(self, content):
        self.content = content
        return self

    def __init__(self, id_, name, theory, pointers):
        self.id: int = id_
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
        super().CanBeUpdated()

    def __init__(self, id_, start, end, chapter, question):
        self.id: int = id_
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

    def __init__(self, id_, name, complition_time, pointer, test, weight: Optional[int] = None):
        self.id: int = id_
        self.name: str = name
        self.complitionTime: datetime.datetime = complition_time
        self.weight: int = weight
        self.pointer: PointerToAnswerViewModel = pointer
        self.test: TestViewModel = test

    @classmethod
    def GetFromId(cls, aId):
        return QuestionViewModel(aId, None, None, None, None)


class QuestionChoiceViewModel(QuestionViewModel):
    def AddAnswers(self, aAnswers: List[AnswerTestViewModel]):
        self.answers_test.extend(aAnswers)
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
        self.correctAnswer = text_answer
        return self

    def __init__(self, id_, name, complition_time, pointer, test,
                 weight: Optional[float] = None, correctAnswer=None, k_misspell=1):
        super().__init__(id_, name, complition_time, pointer, test, weight)
        self.correctAnswer: str = correctAnswer
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

    def __init__(self, id_: int, user, test, answers, startDate, completedDate: Optional[datetime.datetime],
                 note: Optional[str]):
        self.id = id_
        self.user: UserViewModel = user
        self.test: TestViewModel = test
        self.answers: List[AnswerViewModel] = answers
        self.startDate: datetime.datetime = startDate
        self.completedDate: datetime.datetime = completedDate
        self.note: str = note
        self.number_current_question: Optional[QuestionViewModel] = 0


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

    def __init__(self, id_, complitionTime, name, countAttempts, user, theory, shuffle, showAnswer, questions=None):
        self.id: int = id_
        self.complitionTime: datetime.datetime = complitionTime
        self.name: str = name
        self.countAttempts: int = countAttempts
        self.user: UserViewModel = user
        self.theory: TheoryViewModel = theory
        self.shuffle: bool = shuffle
        self.showAnswer: bool = showAnswer
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

    def __init__(self, id_, name, studyTime, tests, chapters, creator):
        self.id: int = id_
        self.name: str = name
        self.studyTime: Optional[datetime.datetime] = studyTime
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
        if self.id is None and self.ip_address is None and self.userAgent is None:
            return Validator(UserViewModel, "id|ipaddress|useragent",
                             "для поиска должно быть заполнено хотя бы одно поле")
        return Validator.default()

    def AddResultTest(self, aResultTest):
        self.resultsTests.append(aResultTest)
        return self

    def AddTest(self, aTest: TestViewModel):
        self.tests.append(aTest)
        return self

    def SetToken(self, token: str):
        self.token = token

    def __init__(self, id_, ipAddress, userAgent, tests, resultsTests):
        self.id: int = id_
        self.ipAddress: int = ipAddress
        self.userAgent: str = userAgent
        self.tests: List[TestViewModel] = tests
        self.resultsTests: List[ResultTestViewModel] = resultsTests
        self.token: str = ""

    @property
    def ip_address(self):
        if self.ipAddress is not None:
            return str(ipaddress.ip_address(self.ipAddress))
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
        answer.complitionTime = self.current_complition_time
        self.__result_test.answers.append(answer)
        self.start_datetime = datetime.datetime.now()
        self.number_current_question += 1

    def complete_test(self) -> ResultTestViewModel:
        self.__completed = True
        return self.__result_test

    @property
    def current_complition_time(self):
        return datetime.datetime.now() - self.start_datetime

    @property
    def current_question(self):
        self._check_completed_result_test()
        return self.questions[self._number_current_question]

    @property
    def number_current_question(self):
        return self._number_current_question + 1

    @number_current_question.setter
    def number_current_question(self, value: int):
        if 0 < value <= len(self.questions):
            self._number_current_question = value - 1
        raise Exception("Установлено некорректный номер вопроса")

    def _check_completed_result_test(self):
        if self.__result_test.completedDate is not None or self.__completed:
            raise Exception("Тест уже завершен")

    def GetViewModel(self) -> 'StatePassingTestViewModel':
        return {"answers": self.__result_test.answers,
                "current_question": self.current_question,
                "test": self.__result_test.test}
