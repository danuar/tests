#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import *
from webapi.ViewModel import ChapterTheoryViewModel


class ChapterLogic(IChapterLogic):
    async def Create(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        return await self._repository.Create(aChapter)

    async def Update(self, aUser, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        return await self._repository.Update(aUser, aChapter)

    async def Get(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        return await self._repository.Get(aChapter)

    async def Delete(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        return await self._repository.Delete(aChapter)

    def LoadChapter(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    def __init__(self):
        self._repository: IChapterRepository = IChapterRepository.__subclasses__()[-1]()
