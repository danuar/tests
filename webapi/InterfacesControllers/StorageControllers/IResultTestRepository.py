#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import ResultTestViewModel, UserViewModel, TestViewModel


class IResultTestRepository(AbstractDbRepository):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    @abstractmethod
    async def Update(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    @abstractmethod
    async def Get(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    @abstractmethod
    async def GetFromUser(self, aUser: UserViewModel, easy_format=False) -> List[ResultTestViewModel]:
        pass

    @abstractmethod
    async def GetFromTest(self, aUser: UserViewModel, aTest: TestViewModel) -> List[ResultTestViewModel]:
        pass

    @abstractmethod
    async def GetFromCreatedUser(self, user, easy_format=False) -> List[ResultTestViewModel]:
        pass
