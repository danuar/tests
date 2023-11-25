#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import IQuestionRepository
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import QuestionViewModel, TestViewModel


class QuestionRepository(IQuestionRepository, AbstractDbRepository):
    async def Create(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def Update(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def Delete(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def Get(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def DeletePointerFromQuestion(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def GetFromTest(self, aTest: TestViewModel) -> List[QuestionViewModel]:
        pass
