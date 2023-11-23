#!/usr/bin/python
# -*- coding: UTF-8 -*-
from StorageControllers import ITestRepository
from StorageControllers import IUserRepository
import TestController
from ViewModel import TestViewModel
from ViewModel import UserViewModel
from BusinessLogicControllers import ITestLogic
from typing import List

class TestLogic(ITestLogic):
	def Create(self, aUser, aTest : TestViewModel) -> TestViewModel:
		pass

	def Update(self, aUser, aTest : TestViewModel) -> TestViewModel:
		pass

	def GetCreated(self, aUser : UserViewModel) -> TestViewModel*:
		pass

	def GetCompleted(self, aUser : UserViewModel) -> TestViewModel*:
		pass

	def Get(self, aTest : TestViewModel) -> TestViewModel:
		pass

	def __init__(self):
		self.___repository : ITestRepository = None
		self.___userRepository : IUserRepository = None
		self._unnamed_IUserRepository_ : IUserRepository = None
		self._unnamed_TestController_ : TestController = None
		self._unnamed_ITestRepository_ : ITestRepository = None
		"""# @AssociationKind Composition"""

