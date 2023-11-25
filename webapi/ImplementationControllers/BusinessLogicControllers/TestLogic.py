#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import ITestLogic, ITestRepository, IUserRepository
from webapi.ViewModel import TestViewModel, UserViewModel


class TestLogic(ITestLogic):
    async def Create(self, aUser, aTest: TestViewModel) -> TestViewModel:
        pass

    async def Update(self, aUser, aTest: TestViewModel) -> TestViewModel:
        pass

    async def GetCreated(self, aUser: UserViewModel) -> List[TestViewModel]:
        pass

    async def GetCompleted(self, aUser: UserViewModel) -> List[TestViewModel]:
        pass

    async def Get(self, aTest: TestViewModel) -> TestViewModel:
        pass

    def __init__(self):
        self._repository: ITestRepository = ITestRepository.__subclasses__()[-1]()
        self._userRepository: IUserRepository = IUserRepository.__subclasses__()[-1]()
