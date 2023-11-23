#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from ViewModel import QuestionViewModel
from ViewModel import TestViewModel
from typing import List

class IQuestionRepository(object):
	"""@Interface"""
	__metaclass__ = ABCMeta
	@abstractmethod
	def Create(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	@abstractmethod
	def Update(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	@abstractmethod
	def Delete(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	@abstractmethod
	def Get(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	@abstractmethod
	def DeletePointerFromQuestion(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	@abstractmethod
	def GetFromTest(self, aTest : TestViewModel) -> QuestionViewModel*:
		pass

