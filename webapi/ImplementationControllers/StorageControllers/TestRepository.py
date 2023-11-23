#!/usr/bin/python
# -*- coding: UTF-8 -*-
from ViewModel import TestViewModel
from ViewModel import UserViewModel
from StorageControllers import ITestRepository
from StorageControllers import AbstractDbRepository
from typing import List

class TestRepository(ITestRepository, AbstractDbRepository):
	def Create(self, aTest : TestViewModel) -> TestViewModel:
		pass

	def Update(self, aTest : TestViewModel) -> TestViewModel:
		pass

	def GetCreated(self, aUser : UserViewModel) -> TestViewModel*:
		pass

	def GetCompleted(self, aUser : UserViewModel) -> TestViewModel*:
		pass

	def Get(self, aTest : TestViewModel) -> TestViewModel:
		pass

	def GetAvailableCountAttempts(self, aUser : UserViewModel, aTest : TestViewModel) -> integer:
		pass

