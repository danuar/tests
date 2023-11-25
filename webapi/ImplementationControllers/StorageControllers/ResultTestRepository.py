#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import IResultTestRepository
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import ResultTestViewModel, UserViewModel, TestViewModel


class ResultTestRepository(IResultTestRepository, AbstractDbRepository):
    async def Create(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    async def Update(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    async def Get(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    async def GetFromUser(self, aUser: UserViewModel) -> List[ResultTestViewModel]:
        pass

    async def GetFromTest(self, aTest: TestViewModel) -> List[ResultTestViewModel]:
        pass
