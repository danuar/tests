#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import ChapterTheoryViewModel


class IChapterLogic(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    @abstractmethod
    async def Update(self, aUser, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    @abstractmethod
    async def Get(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    @abstractmethod
    async def Delete(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    @abstractmethod
    async def LoadChapter(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass
