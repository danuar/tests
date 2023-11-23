#!/usr/bin/python
# -*- coding: UTF-8 -*-
from StorageControllers import IQuestionRepository
from StorageControllers import IUserRepository
import QuestionController
from ViewModel import QuestionViewModel
from ViewModel import TestViewModel
from BusinessLogicControllers import IQuestionLogic
from typing import List

class QuestionLogic(IQuestionLogic):
	def Create(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def Update(self, aUser, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def Delete(self, aUser, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def Get(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def DeletePointerFromQuestion(self, aUser, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def GetFromTest(self, aTest : TestViewModel) -> QuestionViewModel*:
		pass

	def __init__(self):
		self.___repository : IQuestionRepository = None
		self.___userRepository : IUserRepository = None
		self._unnamed_IUserRepository_ : IUserRepository = None
		self._unnamed_QuestionController_ : QuestionController = None
		self._unnamed_IQuestionRepository_ : IQuestionRepository = None
		"""# @AssociationKind Composition"""

