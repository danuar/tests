#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import ITestRepository
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import UserViewModel, TestViewModel


class TestRepository(ITestRepository, AbstractDbRepository):
    async def Create(self, aTest: TestViewModel) -> TestViewModel:
        pass

    async def Update(self, aTest: TestViewModel) -> TestViewModel:
        pass

    async def GetCreated(self, aUser: UserViewModel) -> List[TestViewModel]:
        pass

    async def GetCompleted(self, aUser: UserViewModel) -> List[TestViewModel]:
        pass

    async def Get(self, aTest: TestViewModel) -> TestViewModel:
        pass

    async def GetAvailableCountAttempts(self, aUser: UserViewModel, aTest: TestViewModel) -> int:
        pass
