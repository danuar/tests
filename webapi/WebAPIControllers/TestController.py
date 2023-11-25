#!/usr/bin/python
# -*- coding: UTF-8 -*-
from BusinessLogicControllers import TestLogic
from ViewModel import TestViewModel
from typing import List

class TestController(object):
	def CreateTestPOST(self, aTest : TestViewModel) -> TestViewModel:
		pass

	def UpdateTestPUT(self, aId : integer, aTest : TestViewModel) -> TestViewModel:
		pass

	def CreatedGET(self) -> TestViewModel*:
		pass

	def CompletedGET(self) -> TestViewModel*:
		pass

	def GET(self, aId : int) -> TestViewModel*:
		pass

	def __init__(self):
		self.___logic : TestLogic = None
		self._unnamed_TestLogic_ : TestLogic = None
		"""# @AssociationKind Composition"""

