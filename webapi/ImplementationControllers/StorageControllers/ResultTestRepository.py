#!/usr/bin/python
# -*- coding: UTF-8 -*-
from ViewModel import ResultTestViewModel
from ViewModel import UserViewModel
from ViewModel import TestViewModel
from StorageControllers import IResultTestRepository
from StorageControllers import AbstractDbRepository
from typing import List

class ResultTestRepository(IResultTestRepository, AbstractDbRepository):
	def Create(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	def Update(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	def Get(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	def GetFromUser(self, aUser : UserViewModel) -> ResultTestViewModel*:
		pass

	def GetFromTest(self, aTest : TestViewModel) -> ResultTestViewModel*:
		pass

