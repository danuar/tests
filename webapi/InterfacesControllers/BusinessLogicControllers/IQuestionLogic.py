#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import QuestionViewModel, TestViewModel


class IQuestionLogic(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    @abstractmethod
    async def Update(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    @abstractmethod
    async def Delete(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    @abstractmethod
    async def Get(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    @abstractmethod
    async def DeletePointerFromQuestion(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    @abstractmethod
    async def GetFromTest(self, aTest: TestViewModel) -> List[QuestionViewModel]:
        pass
