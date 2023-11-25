#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import IQuestionLogic, IQuestionRepository, IUserRepository
from webapi.ViewModel import QuestionViewModel, TestViewModel


class QuestionLogic(IQuestionLogic):
    async def Create(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def Update(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def Delete(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def Get(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def DeletePointerFromQuestion(self, aUser, aQuestion: QuestionViewModel) -> QuestionViewModel:
        pass

    async def GetFromTest(self, aTest: TestViewModel) -> List[QuestionViewModel]:
        pass

    def __init__(self):
        self._repository: IQuestionRepository = IQuestionRepository.__subclasses__()[-1]()
        self._userRepository: IUserRepository = IUserRepository.__subclasses__()[-1]()
