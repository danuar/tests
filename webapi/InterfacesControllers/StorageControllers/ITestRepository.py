#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from ViewModel import TestViewModel
from ViewModel import UserViewModel
from typing import List

class ITestRepository(object):
	"""@Interface"""
	__metaclass__ = ABCMeta
	@abstractmethod
	def Create(self, aTest : TestViewModel) -> TestViewModel:
		pass

	@abstractmethod
	def Update(self, aTest : TestViewModel) -> TestViewModel:
		pass

	@abstractmethod
	def GetCreated(self, aUser : UserViewModel) -> TestViewModel*:
		pass

	@abstractmethod
	def GetCompleted(self, aUser : UserViewModel) -> TestViewModel*:
		pass

	@abstractmethod
	def Get(self, aTest : TestViewModel) -> TestViewModel:
		pass

	@abstractmethod
	def GetAvailableCountAttempts(self, aUser : UserViewModel, aTest : TestViewModel) -> integer:
		pass

