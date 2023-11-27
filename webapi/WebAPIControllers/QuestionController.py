#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.InterfacesControllers import IQuestionLogic
from webapi.ViewModel import QuestionViewModel


class QuestionController(object):
    def CreateQuestionPOST(self, aTest: QuestionViewModel) -> QuestionViewModel:
        pass

    def UpdateQuestionPUT(self, aId: int, aTest: QuestionViewModel) -> QuestionViewModel:
        pass

    def GET(self, aId: int) -> QuestionViewModel:
        pass

    def DELETE(self, aId: int) -> QuestionViewModel:
        pass

    def DeletePointerFromQuestionDELETE(self, aId: int) -> QuestionViewModel:
        pass

    def QuestionsGET(self, aTestId: int) -> list[QuestionViewModel]:
        pass

    def __init__(self):
        self._logic: IQuestionLogic = IQuestionLogic.__subclasses__()[-1]()
