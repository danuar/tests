#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import uuid
from typing import Union

from classy_fastapi import post, get, put, delete
from fastapi import Depends

from webapi.InterfacesControllers import IQuestionLogic
from webapi.SchemasModel import QuestionChoiceSchema, QuestionNotCheckSchema, QuestionInputAnswerSchema, \
    QuestionUpdateSchema
from webapi.ViewModel import QuestionViewModel, TestViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user, get_question_logic

QuestionAnnotation = Union[QuestionChoiceSchema, QuestionInputAnswerSchema, QuestionNotCheckSchema]


class QuestionController(AbstractController):

    @post("/question")
    async def create_new_question(self, question: QuestionAnnotation, user=Depends(get_user),
                                  logic=Depends(get_question_logic)) -> QuestionViewModel:
        if question.test is None:
            raise ValueError("Не заполнен id теста, к которому добавляется вопрос")
        res = await logic.Create(user, question.GetViewModel())
        return res

    @put('/question')
    async def update_existing_question(self, question_id: uuid.UUID, question: QuestionUpdateSchema,
                                       user=Depends(get_user),
                                       logic=Depends(get_question_logic)) -> QuestionViewModel:
        return await logic.Update(user, QuestionViewModel.Update(
            question_id, question.name, question.weight, question.complition_time)
                                        .SetPointerToAnswer(question.pointer_to_answer.GetViewModel()))

    @get('/question')
    async def get_question_by_id(self, question_id: uuid.UUID,
                                 logic=Depends(get_question_logic)) -> QuestionViewModel:
        return await logic.Get(QuestionViewModel.GetFromId(question_id))

    @delete('/question')
    async def delete_question_by_id(self, question_id: uuid.UUID, user=Depends(get_user),
                                    logic=Depends(get_question_logic)) -> QuestionViewModel:
        return await logic.Delete(user, QuestionViewModel.GetFromId(question_id))

    @delete('/ptr_from_question')
    async def delete_pointer_from_question_delete(self, question_id: uuid.UUID, user=Depends(get_user),
                                                  logic=Depends(get_question_logic)) -> QuestionViewModel:
        return await logic.DeletePointerFromQuestion(user, QuestionViewModel.GetFromId(question_id))

    @get('/questions')
    async def get_all_questions_by_test_id(self, test_id: uuid.UUID,
                                           logic=Depends(get_question_logic)) -> list[QuestionViewModel]:
        t0 = time.perf_counter()
        res = await logic.GetFromTest(TestViewModel.GetFromId(test_id))
        print(time.perf_counter() - t0)
        return res
