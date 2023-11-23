#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.InterfacesControllers.StorageControllers.IChapterRepository import IChapterRepository
from webapi.ViewModel import ChapterTheoryViewModel


class ChapterRepository(IChapterRepository, AbstractDbRepository):
    def Create(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    def Update(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    def Get(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass

    def Delete(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        pass
