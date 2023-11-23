#!/usr/bin/python
# -*- coding: UTF-8 -*-
from StorageControllers import IChapterRepository
from StorageControllers import IUserRepository
import ChapterController
from ViewModel import ChapterTheoryViewModel
from BusinessLogicControllers import IChapterLogic
from typing import List

class ChapterLogic(IChapterLogic):
	def Create(self, aChapter : ChapterTheoryViewModel) -> ChapterTheoryViewModel:
		pass

	def Update(self, aUser, aChapter : ChapterTheoryViewModel) -> ChapterTheoryViewModel:
		pass

	def Get(self, aChapter : ChapterTheoryViewModel) -> ChapterTheoryViewModel:
		pass

	def Delete(self, aUser, aChapter : ChapterTheoryViewModel) -> ChapterTheoryViewModel:
		pass

	def LoadChapter(self, aChapter : ChapterTheoryViewModel) -> ChapterTheoryViewModel:
		pass

	def __init__(self):
		self.___repository : IChapterRepository = None
		self.___userRepository : IUserRepository = None
		self._unnamed_IUserRepository_ : IUserRepository = None
		self._unnamed_ChapterController_ : ChapterController = None
		self._unnamed_IChapterRepository_ : IChapterRepository = None
		"""# @AssociationKind Composition"""

