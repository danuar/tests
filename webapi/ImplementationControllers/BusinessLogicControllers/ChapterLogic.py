#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import *
from webapi.ViewModel import ChapterTheoryViewModel


class ChapterLogic(IChapterLogic):
    async def Create(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    async def Update(self, aUser, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    async def Get(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    async def Delete(self, aUser, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    def LoadChapter(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    def __init__(self):
        self._repository: IChapterRepository = None
        self._userRepository: IUserRepository = None
