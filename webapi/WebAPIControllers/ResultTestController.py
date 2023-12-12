#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
from typing import List

from classy_fastapi import get, post, put
from fastapi import Depends

from webapi.InterfacesControllers import IResultTestLogic
from webapi.SchemasModel import ResultTestCreateSchema, ResultTestUpdateSchema, AnswerSchema
from webapi.ViewModel import ResultTestViewModel, AnswerViewModel, QuestionViewModel, TestViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user


class ResultTestController(AbstractController):
    @post("/result_test")
    async def start_test(self, result_test: ResultTestCreateSchema, user=Depends(get_user)) -> ResultTestViewModel:
        return await self._logic.Create(
            ResultTestViewModel.Create(user, TestViewModel.GetFromId(result_test.test_id), result_test.note))

    @put("/result_test")
    async def update_result_test(self, aId: uuid.UUID, result_test: ResultTestUpdateSchema) -> ResultTestViewModel:
        return await self._logic.Update(ResultTestViewModel.Update(aId, result_test.completed_date, result_test.note))

    @put("/add_answer")
    async def add_answer_in_result_test(self, result_test_id, answer: AnswerSchema):
        return await self._logic.Update(ResultTestViewModel.GetById(result_test_id)
                                        .AddAnswer(AnswerViewModel
                                                   .Create(answer.complition_time,
                                                           QuestionViewModel.GetFromId(answer.question_id), None,
                                                           answer=answer.text_answer)))

    @get("/result_test")
    async def get_result_by_id(self, aId: int) -> ResultTestViewModel:
        return await self._logic.Get(ResultTestViewModel.GetById(aId))

    @get("/results_test")
    async def get_results_test_by_test_id(self, aTestId: uuid.UUID, user=Depends(get_user)) -> list[ResultTestViewModel]:
        return await self._logic.GetFromTest(user, aTestId)

    @get("/my_results_test")
    async def get_results_test_by_user(self, user=Depends(get_user)) -> list[ResultTestViewModel]:
        return await self._logic.GetFromUser(user)

    @post("/complete_test")
    async def complete_test(self, result_test_id: uuid.UUID, user=Depends(get_user)) -> ResultTestViewModel:
        return await self._logic.CompleteTest(user, ResultTestViewModel.GetById(result_test_id))

    def __init__(self):
        super().__init__()
        self._logic: IResultTestLogic = IResultTestLogic.__subclasses__()[-1]()
