#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers.BusinessLogicControllers.ITheoryLogic import ITheoryLogic
from webapi.InterfacesControllers.StorageControllers.ITheoryRepository import ITheoryRepository
from webapi.ViewModel import TheoryViewModel, ChapterTheoryViewModel, UserViewModel


class TheoryLogic(ITheoryLogic):
    async def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        return await self._repository.Create(aTheory)

    async def Update(self, user: UserViewModel, aTheory: TheoryViewModel) -> TheoryViewModel:
        return await self._repository.Update(aTheory)

    async def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        return await self._repository.Get(aTheory)

    async def GetAllFromUser(self, user: UserViewModel) -> List[TheoryViewModel]:
        return await self._repository.GetAllFromUser(user)

    def LoadChapters(self, aTheory: TheoryViewModel, aPath) -> List[ChapterTheoryViewModel]:
        pass

    def MergeChaptersToPdf(self, aTheory: TheoryViewModel, aPath) -> bool:
        pass

    def __init__(self):
        self._repository: ITheoryRepository = ITheoryRepository.__subclasses__()[-1]()
