#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import TheoryViewModel, ChapterTheoryViewModel


class ITheoryLogic(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    async def Update(self, aUser, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    async def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    @abstractmethod
    async def GetAll(self) -> List[TheoryViewModel]:
        pass

    @abstractmethod
    def LoadChapters(self, aTheory: TheoryViewModel, aPath) -> ChapterTheoryViewModel:
        pass

    @abstractmethod
    def MergeChaptersToPdf(self, aTheory: TheoryViewModel, aPath) -> bool:
        pass
