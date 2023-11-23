#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from ViewModel import ResultTestViewModel
from ViewModel import UserViewModel
from typing import List

class IResultTestLogic(object):
	"""@Interface"""
	__metaclass__ = ABCMeta
	@abstractmethod
	def Create(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	@abstractmethod
	def Update(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	@abstractmethod
	def Get(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

	@abstractmethod
	def GetFromUser(self, aUser : UserViewModel) -> ResultTestViewModel*:
		pass

	@abstractmethod
	def CompleteTest(self, aResult : ResultTestViewModel) -> ResultTestViewModel:
		pass

