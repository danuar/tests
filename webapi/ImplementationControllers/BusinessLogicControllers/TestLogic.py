#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import ITestLogic, ITestRepository, IUserRepository
from webapi.ViewModel import TestViewModel, UserViewModel


class TestLogic(ITestLogic):
    async def Create(self, aTest: TestViewModel) -> TestViewModel:
        return await self._repository.Create(aTest)

    async def Update(self, aUser, aTest: TestViewModel) -> TestViewModel:
        return await self._repository.Update(aTest)

    async def GetCreated(self, aUser: UserViewModel) -> List[TestViewModel]:
        return await self._repository.GetCreated(aUser)

    async def GetCompleted(self, aUser: UserViewModel) -> List[TestViewModel]:
        return await self._repository.GetCompleted(aUser)

    async def Get(self, aTest: TestViewModel) -> TestViewModel:
        return await self._repository.Get(aTest)

    def __init__(self):
        self._repository: ITestRepository = ITestRepository.__subclasses__()[-1]()
