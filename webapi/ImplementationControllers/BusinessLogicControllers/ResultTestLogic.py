#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
from typing import List

from webapi.InterfacesControllers import IResultTestLogic, IResultTestRepository, ITestRepository
from webapi.ViewModel import ResultTestViewModel, UserViewModel, TestViewModel, ResultTestEasyViewModel


class ResultTestLogic(IResultTestLogic):
    async def GetFromCreatedUser(self, user) -> List[ResultTestViewModel]:
        return [i.HideAnswer() for i in await self._repository.GetFromCreatedUser(user)]

    async def Create(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        aResult.start_date = datetime.datetime.now()
        if (await self._test_repository.GetAvailableCountAttempts(aResult.user, aResult.test)) == 0:
            raise Exception("Вы потратили все попытки на прохождение данного теста")
        return await self._repository.Create(aResult)

    async def Update(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        return await self._repository.Update(aUser, aResult)

    async def Get(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        return (await self._repository.Get(aUser, aResult)).HideAnswer()

    async def GetFromUser(self, aUser: UserViewModel) -> List[ResultTestViewModel]:
        return [i.HideAnswer() for i in await self._repository.GetFromUser(aUser)]

    async def CompleteTest(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        aResult.completed_date = datetime.datetime.now()
        return (await self._repository.Update(aUser, aResult)).HideAnswer()

    async def GetFromTest(self, aUser: UserViewModel, aTest: TestViewModel) -> List[ResultTestViewModel]:
        return [i.HideAnswer() for i in await self._repository.GetFromTest(aUser, aTest)]

    async def GetFromCreatedUserInEasyFormat(self, user: UserViewModel) -> list[ResultTestEasyViewModel]:
        return await self._repository.GetFromCreatedUser(user, True)

    async def GetFromUserInEasyFormat(self, user: UserViewModel) -> list[ResultTestEasyViewModel]:
        return await self._repository.GetFromUser(user, True)

    def __init__(self):
        self._repository: IResultTestRepository = IResultTestRepository.__subclasses__()[-1]()
        self._test_repository: ITestRepository = ITestRepository.__subclasses__()[-1]()
