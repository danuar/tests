#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod

from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import ChapterTheoryViewModel, UserViewModel


class IChapterRepository(AbstractDbRepository):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    @abstractmethod
    async def Update(self, user: UserViewModel, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    @abstractmethod
    async def Get(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    @abstractmethod
    async def Delete(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass
