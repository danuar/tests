#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
from typing import List

from webapi.InterfacesControllers import IResultTestLogic, IResultTestRepository, IUserRepository, ITestRepository
from webapi.ViewModel import ResultTestViewModel, UserViewModel, TestViewModel


class ResultTestLogic(IResultTestLogic):
    async def Create(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        aResult.startDate = datetime.datetime.now()
        if (await self._test_repository.GetAvailableCountAttempts(aResult.user, aResult.test)) == 0:
            raise Exception("Вы потратили все попытки на прохождение данного теста")
        return await self._repository.Create(aResult)

    async def Update(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        return await self._repository.Update(aUser, aResult)

    async def Get(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        return await self._repository.Get(aUser, aResult)

    async def GetFromUser(self, aUser: UserViewModel) -> List[ResultTestViewModel]:
        return await self._repository.GetFromUser(aUser)

    async def CompleteTest(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        aResult.completedDate = datetime.datetime.now()
        return await self._repository.Update(aUser, aResult)

    async def GetFromTest(self, aUser: UserViewModel, aTest: TestViewModel) -> List[ResultTestViewModel]:
        return await self._repository.GetFromTest(aUser, aTest)

    def __init__(self):
        self._repository: IResultTestRepository = IResultTestRepository.__subclasses__()[-1]()
        self._test_repository: ITestRepository = ITestRepository.__subclasses__()[-1]()
