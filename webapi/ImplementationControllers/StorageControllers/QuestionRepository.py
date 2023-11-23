#!/usr/bin/python
# -*- coding: UTF-8 -*-
from ViewModel import QuestionViewModel
from ViewModel import TestViewModel
from StorageControllers import IQuestionRepository
from StorageControllers import AbstractDbRepository
from typing import List

class QuestionRepository(IQuestionRepository, AbstractDbRepository):
	def Create(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def Update(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def Delete(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def Get(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def DeletePointerFromQuestion(self, aQuestion : QuestionViewModel) -> QuestionViewModel:
		pass

	def GetFromTest(self, aTest : TestViewModel) -> QuestionViewModel*:
		pass

