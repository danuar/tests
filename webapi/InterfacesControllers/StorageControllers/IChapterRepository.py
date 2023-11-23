#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from ViewModel import ChapterTheoryViewModel
from typing import List

class IChapterRepository(object):
	"""@Interface"""
	__metaclass__ = ABCMeta
	@abstractmethod
	def Create(self, aChapter : ChapterTheoryViewModel) -> ChapterTheoryViewModel:
		pass

	@abstractmethod
	def Update(self, aChapter : ChapterTheoryViewModel) -> ChapterTheoryViewModel:
		pass

	@abstractmethod
	def Get(self, aChapter : ChapterTheoryViewModel) -> ChapterTheoryViewModel:
		pass

	@abstractmethod
	def Delete(self, aChapter : ChapterTheoryViewModel) -> ChapterTheoryViewModel:
		pass

