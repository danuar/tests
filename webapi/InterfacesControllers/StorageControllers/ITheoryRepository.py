#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import TheoryViewModel, UserViewModel


class ITheoryRepository(AbstractDbRepository):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    async def Update(self, user: UserViewModel, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    async def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    async def GetAllFromUser(self, user: UserViewModel) -> List[TheoryViewModel]:
        pass
