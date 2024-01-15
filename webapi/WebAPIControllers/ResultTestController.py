#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid

from classy_fastapi import get, post, put
from fastapi import Depends

from webapi.InterfacesControllers import IResultTestLogic
from webapi.SchemasModel import ResultTestCreateSchema, ResultTestUpdateSchema, AnswerSchema, AnswerWithMark
from webapi.ViewModel import ResultTestViewModel, AnswerViewModel, QuestionViewModel, TestViewModel, \
    AnswerTestViewModel, ResultTestEasyViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user, get_result_test_logic


class ResultTestController(AbstractController):
    @post("/result_test")
    async def start_test(self, result_test: ResultTestCreateSchema, user=Depends(get_user),
                         logic=Depends(get_result_test_logic)) -> ResultTestViewModel:
        return await logic.Create(
            ResultTestViewModel.Create(user, TestViewModel.GetFromId(result_test.test_id), result_test.note))

    @put("/result_test")
    async def update_result_test(self, aId: uuid.UUID, result_test: ResultTestUpdateSchema, user=Depends(get_user),
                                 logic=Depends(get_result_test_logic)) -> ResultTestViewModel:
        return await logic.Update(user,
                                  ResultTestViewModel.Update(aId, result_test.completed_date, result_test.note))

    @put("/add_answer")
    async def add_answer_in_result_test(self, result_test_id: uuid.UUID, answer: AnswerSchema, user=Depends(get_user),
                                        logic=Depends(get_result_test_logic)):
        return await logic.Update(user, ResultTestViewModel.GetById(result_test_id)
                                  .AddAnswer(
            AnswerViewModel.Create(answer.complition_time,
                                   QuestionViewModel.GetFromId(answer.question_id), None,
                                   answer=answer.text_answer)
            .AddAnswersTests([AnswerTestViewModel.FromId(i) for i in answer.answers_test])))

    @get("/result_test")
    async def get_result_by_id(self, aId: uuid.UUID, user=Depends(get_user),
                               logic=Depends(get_result_test_logic)) -> ResultTestViewModel:
        return await logic.Get(user, ResultTestViewModel.GetById(aId))

    @get("/results_test")
    async def get_results_test_by_test_id(self, aTestId: uuid.UUID, user=Depends(get_user),
                                          logic=Depends(get_result_test_logic)) -> list[ResultTestViewModel]:
        return await logic.GetFromTest(user, aTestId)

    @get("/results_test_by_created_tests")
    async def get_results_test_by_created_tests(self, user=Depends(get_user),
                                                logic=Depends(get_result_test_logic)) -> list[ResultTestViewModel]:
        return await logic.GetFromCreatedUser(user)

    @get("/my_results_test")
    async def get_results_test_by_user(self, user=Depends(get_user),
                                       logic=Depends(get_result_test_logic)) -> list[ResultTestViewModel]:
        return await logic.GetFromUser(user)

    @post("/complete_test")
    async def complete_test(self, result_test_id: uuid.UUID, user=Depends(get_user),
                            logic=Depends(get_result_test_logic)) -> ResultTestViewModel:
        return await logic.CompleteTest(user, ResultTestViewModel.GetById(result_test_id))

    @put("/change_note")
    async def change_note_in_result_test(self, result_test_id: uuid.UUID, note: str, user=Depends(get_user),
                                         logic=Depends(get_result_test_logic)):
        return await logic.Update(user, ResultTestViewModel.Update(result_test_id, None, note))

    @put("/mark_for_question_not_check")
    async def add_marks_for_all_answers(self, answers: list[AnswerWithMark], user=Depends(get_user),
                                        logic=Depends(get_result_test_logic)):
        return await logic.Update(user, ResultTestViewModel.GetById(None)
                                  .AddAnswers([AnswerViewModel.Update(i.answer_id, i.mark) for i in answers]))

    @get("/results_test_by_created_tests_easy")
    async def get_results_test_by_created_tests_in_easy_format(self, user=Depends(get_user),
                                                               logic=Depends(get_result_test_logic)
                                                               ) -> list[ResultTestEasyViewModel]:
        return await logic.GetFromCreatedUserInEasyFormat(user)

    @get("/results_test_by_user_easy")
    async def get_results_test_by_user_in_easy_format(self, user=Depends(get_user),
                                                      logic=Depends(get_result_test_logic)
                                                      ) -> list[ResultTestEasyViewModel]:
        return await logic.GetFromUserInEasyFormat(user)
