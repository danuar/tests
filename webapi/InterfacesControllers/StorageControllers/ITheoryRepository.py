#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import TheoryViewModel


class ITheoryRepository(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    async def Update(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    async def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    async def GetAll(self) -> List[TheoryViewModel]:
        pass
