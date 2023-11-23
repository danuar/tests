#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from ViewModel import TheoryViewModel
from typing import List

class ITheoryLogic(object):
	"""@Interface"""
	__metaclass__ = ABCMeta
	@abstractmethod
	def Create(self, aTheory : TheoryViewModel) -> TheoryViewModel:
		pass

	@abstractmethod
	def Update(self, aUser, aTheory : TheoryViewModel) -> TheoryViewModel:
		pass

	@abstractmethod
	def Get(self, aTheory : TheoryViewModel) -> TheoryViewModel:
		pass

	@abstractmethod
	def GetAll(self) -> TheoryViewModel*:
		pass

	@abstractmethod
	def LoadChapters(self, aTheory : TheoryViewModel, aPath) -> ChapterViewModel*:
		pass

	@abstractmethod
	def MergeChaptersToPdf(self, aTheory : TheoryViewModel, aPath) -> long:
		pass

