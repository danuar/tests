#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.InterfacesControllers.StorageControllers.IChapterRepository import IChapterRepository
from webapi.ViewModel import ChapterTheoryViewModel


class ChapterRepository(IChapterRepository, AbstractDbRepository):
    async def Create(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    async def Update(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    async def Get(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    async def Delete(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass
