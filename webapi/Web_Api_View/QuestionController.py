#!/usr/bin/python
# -*- coding: UTF-8 -*-
from BusinessLogicControllers import QuestionLogic
from ViewModel import QuestionViewModel
from typing import List

class QuestionController(object):
	def CreateQuestionPOST(self, aTest : QuestionViewModel) -> QuestionViewModel:
		pass

	def UpdateQuestionPUT(self, aId : integer, aTest : QuestionViewModel) -> QuestionViewModel:
		pass

	def GET(self, aId : int) -> QuestionViewModel:
		pass

	def DELETE(self, aId : int) -> QuestionViewModel:
		pass

	def DeletePointerFromQuestionDELETE(self, aId : int) -> QuestionViewModel:
		pass

	def QuestionsGET(self, aTestId : integer) -> QuestionViewModel*:
		pass

	def __init__(self):
		self.___logic : QuestionLogic = None
		self._unnamed_QuestionLogic_ : QuestionLogic = None
		"""# @AssociationKind Composition"""

