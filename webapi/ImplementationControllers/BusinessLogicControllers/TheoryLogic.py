#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers.BusinessLogicControllers.ITheoryLogic import ITheoryLogic
from webapi.InterfacesControllers.StorageControllers.ITheoryRepository import ITheoryRepository
from webapi.InterfacesControllers.StorageControllers.IUserRepository import IUserRepository
from webapi.ViewModel import TheoryViewModel, ChapterTheoryViewModel


class TheoryLogic(ITheoryLogic):
    def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    def Update(self, aUser, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    def GetAll(self) -> List[TheoryViewModel]:
        pass

    def LoadChapters(self, aTheory: TheoryViewModel, aPath) -> List[ChapterTheoryViewModel]:
        pass

    def MergeChaptersToPdf(self, aTheory: TheoryViewModel, aPath) -> bool:
        pass

    def __init__(self):
        self._repository: ITheoryRepository = None
        self._userRepository: IUserRepository = None
