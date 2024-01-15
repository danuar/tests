#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import ITestLogic, ITestRepository
from webapi.ViewModel import TestViewModel, UserViewModel


class TestLogic(ITestLogic):
    async def GetAvailableTests(self, aUser: UserViewModel):
        return await self._repository.GetAvailableTests(aUser)

    async def GetAvailableCountAttempts(self, aUser: UserViewModel, aTest: TestViewModel) -> int:
        return await self._repository.GetAvailableCountAttempts(aUser, aTest)

    async def Create(self, aTest: TestViewModel) -> TestViewModel:
        return await self._repository.Create(aTest)

    async def Update(self, aUser: UserViewModel, aTest: TestViewModel) -> TestViewModel:
        return await self._repository.Update(aUser, aTest)

    async def GetCreated(self, aUser: UserViewModel) -> List[TestViewModel]:
        return [i.HideAnswer() for i in await self._repository.GetCreated(aUser)]

    async def GetCompleted(self, aUser: UserViewModel) -> List[TestViewModel]:
        return [i.HideAnswer() for i in await self._repository.GetCompleted(aUser)]

    async def Get(self, aTest: TestViewModel) -> TestViewModel:
        return (await self._repository.Get(aTest)).HideAnswer()
