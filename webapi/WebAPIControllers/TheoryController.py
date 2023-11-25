#!/usr/bin/python
# -*- coding: UTF-8 -*-
from BusinessLogicControllers import TheoryLogic
from ViewModel import TheoryViewModel
from typing import List

class TheoryController(object):
	def CreateTheoryPOST(self, aTest : TheoryViewModel) -> TheoryViewModel:
		pass

	def UpdateTheoryPUT(self, aId : integer, aTest : TheoryViewModel) -> TheoryViewModel:
		pass

	def GET(self, aId : int) -> TheoryViewModel:
		pass

	def pdfGET(self, aId : int) -> File:
		pass

	def htmlChaptersGET(self, aId : int) -> File*:
		pass

	def TheoriesGET(self) -> TheoryViewModel*:
		pass

	def __init__(self):
		self.___logic : TheoryLogic = None
		self._unnamed_TheoryLogic_ : TheoryLogic = None
		"""# @AssociationKind Composition"""

