#!/usr/bin/python
# -*- coding: UTF-8 -*-
from StorageControllers import IResultTestRepository
from StorageControllers import IUserRepository
import ResultTestController
from ViewModel import ResultTestViewModel
from ViewModel import UserViewModel
from ViewModel import TestViewModel
from BusinessLogicControllers import IResultTestLogic
from typing import List

class ResultTestLogic(IResultTestLogic):
	def Create(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	def Update(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	def Get(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	def GetFromUser(self, aUser : UserViewModel) -> ResultTestViewModel*:
		pass

	def CompleteTest(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	def GetFromTest(self, aUser, aTest : TestViewModel) -> ResultTestViewModel*:
		pass

	def __init__(self):
		self.___repository : IResultTestRepository = None
		self.___userRepository : IUserRepository = None
		self._unnamed_IUserRepository_ : IUserRepository = None
		self._unnamed_ResultTestController_ : ResultTestController = None
		self._unnamed_IResultTestRepository_ : IResultTestRepository = None
		"""# @AssociationKind Composition"""

