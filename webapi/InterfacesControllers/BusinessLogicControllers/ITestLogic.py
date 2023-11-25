#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import TestViewModel, UserViewModel


class ITestLogic(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aUser, aTest: TestViewModel) -> TestViewModel:
        pass

    @abstractmethod
    async def Update(self, aUser, aTest: TestViewModel) -> TestViewModel:
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
