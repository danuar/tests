#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import TheoryViewModel


class ITheoryRepository(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    def Update(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    def GetAll(self) -> List[TheoryViewModel]:
        pass
