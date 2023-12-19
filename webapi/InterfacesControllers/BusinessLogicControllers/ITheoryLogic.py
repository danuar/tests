#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import TheoryViewModel, ChapterTheoryViewModel, UserViewModel


class ITheoryLogic(object):
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
    async def GetAllFromUser(self, user: UserViewModel, get_content: bool) -> List[TheoryViewModel]:
        pass

    @abstractmethod
    async def MergeChaptersToPdf(self, aTheory: TheoryViewModel, aPath=None) -> str:
        pass
