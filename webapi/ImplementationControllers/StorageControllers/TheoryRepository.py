#!/usr/bin/python
# -*- coding: UTF-8 -*-
from ViewModel import TheoryViewModel
from StorageControllers import ITheoryRepository
from StorageControllers import AbstractDbRepository
from typing import List

class TheoryRepository(ITheoryRepository, AbstractDbRepository):
	def Create(self, aTheory : TheoryViewModel) -> TheoryViewModel:
		pass

	def Update(self, aTheory : TheoryViewModel) -> TheoryViewModel:
		pass

	def Get(self, aTheory : TheoryViewModel) -> TheoryViewModel:
		pass

	def GetAll(self) -> TheoryViewModel*:
		pass

