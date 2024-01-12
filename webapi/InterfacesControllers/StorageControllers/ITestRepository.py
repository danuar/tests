#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import TestViewModel, UserViewModel


class ITestRepository(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aTest: TestViewModel) -> TestViewModel:
        pass

    @abstractmethod
    async def Update(self, aUser: UserViewModel, aTest: TestViewModel) -> TestViewModel:
        pass

    @abstractmethod
    async def GetCreated(self, aUser: UserViewModel) -> List[TestViewModel]:
        pass

    @abstractmethod
    async def GetCompleted(self, aUser: UserViewModel) -> List[TestViewModel]:
        pass

    @abstractmethod
    async def Get(self, aTest: TestViewModel) -> TestViewModel:
        pass

    @abstractmethod
    async def GetAvailableCountAttempts(self, aUser: UserViewModel, aTest: TestViewModel) -> int:
        pass

    @abstractmethod
    async def GetAvailableTests(self, aUser):
        pass
