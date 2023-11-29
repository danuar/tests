#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import IQuestionLogic, IQuestionRepository, IUserRepository
from webapi.ViewModel import QuestionViewModel, TestViewModel


class QuestionLogic(IQuestionLogic):
    async def Create(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        return await self._repository.Create(aUser, aQuestion)

    async def Update(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        return await self._repository.Update(aUser, aQuestion)

    async def Delete(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        return await self._repository.Delete(aUser, aQuestion)

    async def Get(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        return await self._repository.Get(aQuestion)

    async def DeletePointerFromQuestion(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        return await self._repository.DeletePointerFromQuestion(aUser, aQuestion)

    async def GetFromTest(self, aTest: TestViewModel) -> List[QuestionViewModel]:
        return await self._repository.GetFromTest(aTest)

    def __init__(self):
        self._repository: IQuestionRepository = IQuestionRepository.__subclasses__()[-1]()
