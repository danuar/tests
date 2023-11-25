#!/usr/bin/python
# -*- coding: UTF-8 -*-
from BusinessLogicControllers import ResultTestLogic
from ViewModel import ResultTestViewModel
from typing import List

class ResultTestController(object):
	def CreateResultTestPOST(self, aTest : ResultTestViewModel) -> ResultTestViewModel:
		pass

	def UpdateResultTestPUT(self, aId : integer, aTest : ResultTestViewModel) -> ResultTestViewModel:
		pass

	def GET(self, aId : int) -> ResultTestViewModel:
		pass

	def ResultTestGET(self, aTestId : integer) -> ResultTestViewModel*:
		pass

	def ResultTestGET(self) -> ResultTestViewModel*:
		pass

	def CompleteTest(self, aTestId : integer) -> ResultTestViewModel:
		pass

	def __init__(self):
		self.___logic : ResultTestLogic = None
		self._unnamed_ResultTestLogic_ : ResultTestLogic = None
		"""# @AssociationKind Composition"""

