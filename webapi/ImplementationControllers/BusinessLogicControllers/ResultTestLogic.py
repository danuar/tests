#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import IResultTestLogic, IResultTestRepository, IUserRepository
from webapi.ViewModel import ResultTestViewModel, UserViewModel, TestViewModel


class ResultTestLogic(IResultTestLogic):
    async def Create(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    async def Update(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    async def Get(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    async def GetFromUser(self, aUser: UserViewModel) -> List[ResultTestViewModel]:
        pass

    async def CompleteTest(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    async def GetFromTest(self, aUser, aTest: TestViewModel) -> List[ResultTestViewModel]:
        pass

    def __init__(self):
        self._repository: IResultTestRepository = IResultTestRepository.__subclasses__()[-1]()
        self._userRepository: IUserRepository = IUserRepository.__subclasses__()[-1]()
