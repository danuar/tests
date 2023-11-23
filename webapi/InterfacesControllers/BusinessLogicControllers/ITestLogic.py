#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from ViewModel import TestViewModel
from ViewModel import UserViewModel
from typing import List

class ITestLogic(object):
	"""@Interface"""
	__metaclass__ = ABCMeta
	@abstractmethod
	def Create(self, aUser, aTest : TestViewModel) -> TestViewModel:
		pass

	@abstractmethod
	def Update(self, aUser, aTest : TestViewModel) -> TestViewModel:
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

