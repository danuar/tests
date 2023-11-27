#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipaddress
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

    def __init__(self, id_, name, theory, pointers):
        self.id: int = id_
        self.name: str = name
        self.theory: TheoryViewModel = theory
        self.pointers: List[PointerToAnswerViewModel] = pointers


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
    @staticmethod
    def Create(aName: str, aWeight, aComplitionTime, aTest):
        return QuestionViewModel(None, aName, aComplitionTime, None, aTest, aWeight)

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


class QuestionChoiceViewModel(QuestionViewModel):
    def AddAnswers(self, aAnswers: List[AnswerTestViewModel]):
        self.answers_test.extend(aAnswers)
        return self

    def __init__(self, id_, name, complition_time, pointer, test, answers: List[AnswerTestViewModel],
                 weight: Optional[int] = None):
        super().__init__(id_, name, complition_time, pointer, test, weight)
        self.answers_test = answers


class QuestionInputAnswerViewModel(QuestionViewModel):
    @staticmethod
    def Create(aCorrectAnswer, aKMisspell: float, aName: str, aComplitionTime, aTest,
               weight: Optional[float] = None) -> QuestionViewModel:
        return QuestionInputAnswerViewModel(aName, aComplitionTime, None, aTest, weight, aCorrectAnswer, aKMisspell)

    def __init__(self, id_, name, complition_time, pointer, test, correctAnswer, k_misspell,
                 weight: Optional[float] = None):
        super().__init__(id_, name, complition_time, pointer, test, weight)
        self.correctAnswer: str = correctAnswer
        self.k_misspell: float = k_misspell


class QuestionNotCheckViewModel(QuestionViewModel):
    pass


class ResultTestViewModel(AbstractModelView):
    @staticmethod
    def Create(aUser, aTest):
        return ResultTestViewModel(None, aUser, aTest, [], datetime.datetime.now(), None, None)

    @staticmethod
    def Update(aId: int, aCompletedDate: datetime.datetime, aNote: str):
        return ResultTestViewModel(aId, None, None, [], None, aCompletedDate, aNote)

    def CanBeCreated(self) -> Validator:
        pass

    def CanBeUpdated(self) -> Validator:
        pass

    def AddAnswer(self, aAnswer: AnswerViewModel):
        self.answers.append(aAnswer)

    def __init__(self, id_: int, user, test, answers, startDate, completedDate: Optional[datetime.datetime],
                 note: Optional[str]):
        self.id = id_
        self.user: UserViewModel = user
        self.test: TestViewModel = test
        self.answers: List[AnswerViewModel] = answers
        self.startDate: datetime.datetime = startDate
        self.completedDate: datetime.datetime = completedDate
        self.note: str = note


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

    def CanBeCreated(self) -> Validator:
        return Validator.default()  # todo реализовать валидацию всех моделей

    def CanBeUpdated(self) -> Validator:
        return Validator.default()

    def __init__(self, id_, complitionTime, name, countAttempts, user, theory, shuffle, showAnswer):
        self.id: int = id_
        self.complitionTime: datetime.datetime = complitionTime
        self.name: str = name
        self.countAttempts: int = countAttempts
        self.user: UserViewModel = user
        self.theory: TheoryViewModel = theory
        self.shuffle: bool = shuffle
        self.showAnswer: bool = showAnswer


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

