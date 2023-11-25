#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import ITheoryRepository
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import TheoryViewModel


class TheoryRepository(ITheoryRepository, AbstractDbRepository):
    async def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    async def Update(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    async def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        pass

    async def GetAll(self) -> List[TheoryViewModel]:
        pass
