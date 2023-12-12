#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List, Union

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
    async def LoadChapter(self, aChapter: ChapterTheoryViewModel, overwrite: bool, delegate_write: bool) -> ChapterTheoryViewModel:
        pass

    @abstractmethod
    async def GetContentByChapter(self, aChapter: ChapterTheoryViewModel, get_path_to_file=True) -> (
            Union)[list[str], list[ChapterTheoryViewModel]]:
        pass
