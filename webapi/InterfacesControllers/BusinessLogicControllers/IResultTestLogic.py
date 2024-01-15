#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.InterfacesControllers.StorageControllers import IResultTestRepository, ITestRepository
from webapi.ViewModel import ResultTestViewModel, UserViewModel, ResultTestEasyViewModel


class IResultTestLogic(object):
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
    async def GetFromUser(self, aUser: UserViewModel) -> List[ResultTestViewModel]:
        pass

    @abstractmethod
    async def GetFromTest(self, aUser: UserViewModel, aTestId) -> List[ResultTestViewModel]:
        pass

    @abstractmethod
    async def CompleteTest(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    @abstractmethod
    async def GetFromCreatedUser(self, user):
        pass

    @abstractmethod
    async def GetFromCreatedUserInEasyFormat(self, user: UserViewModel) -> list[ResultTestEasyViewModel]:
        pass

    @abstractmethod
    async def GetFromUserInEasyFormat(self, user: UserViewModel) -> list[ResultTestEasyViewModel]:
        pass

    def __init__(self, repository: IResultTestRepository, test_repository: ITestRepository):
        self._repository = repository
        self._test_repository = test_repository
