#!/usr/bin/python
# -*- coding: UTF-8 -*-
from BusinessLogicControllers import ChapterLogic
from typing import List

class ChapterController(object):
	def CreateChapterPOST(self, aTest : ViewModel.ChapterViewModel) -> ViewModel.ChapterViewModel:
		pass

	def UpdateChapterPUT(self, aId : integer, aTest : ViewModel.ChapterViewModel) -> ViewModel.ChapterViewModel:
		pass

	def GET(self, aId : int) -> ViewModel.ChapterViewModel:
		pass

	def DELETE(self, aId : int) -> ViewModel.ChapterViewModel:
		pass

	def htmlGET(self, aId : int) -> File:
		pass

	def __init__(self):
		self.___logic : ChapterLogic = None
		self._unnamed_ChapterLogic_ : ChapterLogic = None
		"""# @AssociationKind Composition"""

