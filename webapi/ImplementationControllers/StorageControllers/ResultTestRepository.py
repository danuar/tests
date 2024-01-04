#!/usr/bin/python
# -*- coding: UTF-8 -*-
import asyncio
import datetime
import difflib
import operator
import uuid
from functools import reduce
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncResult
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.base import Options

from webapi.InterfacesControllers import IResultTestRepository, ICachedService
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import ResultTestViewModel, UserViewModel, TestViewModel, ResultTestEasyViewModel
from webapi.db import DbSession, ResultTest, Test, Question, Answer, answer_user_by_answer_test, Theory

_cached_service: ICachedService = ICachedService.__subclasses__()[-1]()


class ResultTestRepository(IResultTestRepository, AbstractDbRepository):

    async def GetFromCreatedUser(self, user, easy_format=False):
        created_test_ids = (await self.session.scalars(select(Test.id).where(Test.creator_id == user.id)))
        result = await self.session.execute(select(ResultTest)
                                            .where(ResultTest.test_id.in_(created_test_ids))
                                            .options(*self._get_options()))
        return [i.GetViewModel() for i in result.unique().scalars()] if not easy_format else self._get_in_easy_format(
            result)

    @staticmethod
    def _get_in_easy_format(result) -> list[ResultTestEasyViewModel]:
        return [ResultTestEasyViewModel(i.id, i.completed_date, i.test.name,
                                        sum(j.mark for j in i.answers if j.mark),
                                        sum(j.weight for j in i.test.questions),
                                        reduce(operator.add, (
                                            datetime.timedelta(
                                                hours=j.complition_time.hour,
                                                minutes=j.complition_time.minute,
                                                seconds=j.complition_time.second)
                                            for j in i.test.questions if j.complition_time), datetime.timedelta()),
                                        i.note,
                                        any(j.mark is None for j in i.answers)) for i in result.unique().scalars()]

    def __init__(self):
        super().__init__()
        self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]()
        self.session = DbSession().async_session

    async def Create(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        result = ResultTest.CreateFrom(aResult)
        self.session.add(result)

        await self.session.commit()
        result.test = await self.session.get(Test, result.test_id, self._get_options_question())
        if result.test.completion_time:
            mn = datetime.datetime.min
            diff = datetime.datetime.combine(mn, result.test.completion_time) - mn
            asyncio.get_event_loop().create_task(self._complete_result_test(diff.total_seconds(), result))
        return result.GetViewModel()

    async def _complete_result_test(self, delay, result: ResultTest):
        await asyncio.sleep(delay)
        async with DbSession().session().begin() as transaction:
            await transaction.session.execute(update(ResultTest)
                                              .where(ResultTest.id == result.id)
                                              .values(completed_date=datetime.datetime.now()))
            await transaction.commit()
            self.cachedService.Remove(f"StatePassingTest.{result.user_id}")

    async def _set_mark(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        query = await self.session.execute(select(Answer)
                                           .where(Answer.id.in_(i.id for i in aResult.answers))
                                           .options(joinedload(Answer.result_test).joinedload(ResultTest.test),
                                                    joinedload(Answer.question).joinedload(
                                                        Question.question_not_check)))
        answers_db: dict[uuid.UUID, Answer] = {i.id: i for i in query.unique().scalars()}
        for answer in aResult.answers:
            answer_db: Answer = answers_db.get(answer.id, None)
            if answer_db is None:
                raise Exception("Неверно задан id ответа")
            if answer_db.result_test.test.creator_id != aUser.id:
                raise Exception("Только создатель теста может проставлять баллы за ответы на тест")
            if answer_db.question.question_not_check is None:
                raise Exception(f"На вопрос {answer_db.question} ответ проставляется автоматически")
            if answer_db.mark is not None:
                raise Exception(f"На вопрос {answer_db.question} уже выставлен балл")
            if not (0 <= answer.mark <= answer_db.question.weight):
                raise Exception(f"Диапазон выставления баллов на данный вопрос от 0 до {answer_db.question.mark}")
            answer_db.mark = answer.mark
        await self.session.commit()
        return aResult

    async def Update(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        if aResult.id is None:  # ответы с проставленными баллами
            if not all([i.mark and i.id for i in aResult.answers]):
                raise Exception("Не проставлены баллы")
            return await self._set_mark(aUser, aResult)

        result_db = await self._get(aUser.id, aResult.id, [
            selectinload(ResultTest.answers).joinedload(Answer.answers_test),
            selectinload(ResultTest.test).joinedload(Test.theory),
            selectinload(ResultTest.test).joinedload(Test.questions),
        ])
        result_db.note = aResult.note
        print(result_db.test, result_db.test.theory, result_db.test.theory.chapters, result_db.answers, [i.answers_test for i in result_db.answers])
        if result_db.completed_date:
            if aUser.id == result_db.user_id and aResult.note is not None:
                await self.session.commit()
                return aResult
            raise Exception("Нельзя изменить результаты уже пройденного теста")
        test = result_db.test
        questions_db = (await self.session.execute(select(Question)
                                                   .where(Question.id.in_(i.id for i in test.questions))
                                                   .options(joinedload(Question.pointer_to_answer),
                                                            joinedload(Question.question_input_answer),
                                                            joinedload(Question.question_choice),
                                                            joinedload(Question.question_not_check)))
                        ).unique().scalars()
        questions = {i.id: i for i in questions_db}
        answers = {i.id: i for i in result_db.answers}
        link_answers_by_answers_test = []
        for answer in aResult.answers:
            answer.mark = 0
            if answer.id in answers:
                raise Exception("Ответ на вопрос уже добавлен")
            if answer.question.id not in questions:
                raise Exception("В тесте нет вопроса на который добавляется ответ")
            question = questions[answer.question.id]
            if test.completion_time is None and answer.complition_time > question.complition_time:
                continue  # Превышено время ответа на вопрос
            if question.question_input_answer:
                ratio = question.question_input_answer.k_misspell
                result_ratio = difflib.SequenceMatcher(None, answer.text_answer,
                                                       question.question_input_answer.correct_answer, True).ratio()
                if result_ratio > ratio:
                    answer.mark = question.weight
            elif question.question_choice:
                corrects = {i.id for i in question.question_choice.answers_test if i.correct}
                count_correct = sum(1 if i.id in corrects else -1 for i in answer.answers_test)
                if count_correct > 0:
                    answer.mark = count_correct * question.weight // len(corrects)
            elif question.question_not_check:
                answer.mark = None
            link_answers_by_answers_test.append([Answer.CreateFrom(answer), answer.answers_test])
            result_db.answers.append(link_answers_by_answers_test[-1][0])
        result_db.completed_date = aResult.completed_date
        await self.session.flush()
        await self.session.execute(answer_user_by_answer_test.insert([
            {"answer_id": answer.id, "answer_test_id": i.id} for answer, answers_test in link_answers_by_answers_test
            for i in answers_test
        ]))
        await self.session.commit()
        for answer in result_db.answers:
            answer.question = questions[answer.question_id]
        return result_db.GetViewModel()

    async def Get(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        return (await self._get(aUser.id, aResult.id, self._get_options())).GetViewModel()

    async def GetFromUser(self, aUser: UserViewModel, easy_format=False) -> List[ResultTestViewModel]:
        result: AsyncResult = await self.session.execute(select(ResultTest)
                                                         .where(ResultTest.user_id == aUser.id)
                                                         .options(*self._get_options()))
        return [i.GetViewModel() for i in result.unique().scalars()] if not easy_format else self._get_in_easy_format(
            result)

    async def GetFromTest(self, aUser: UserViewModel, aTest: TestViewModel) -> List[ResultTestViewModel]:
        test: Test = await self.session.get(Test, aTest.id, options=[joinedload(Test.results_tests)])
        if test.creator_id != aUser.id:
            raise Exception("Только создатель теста может получить результаты теста")
        return [i.GetViewModel() for i in test.results_tests]

    async def _get(self, user_id, result_id, options: Optional[list[Options]] = None) -> ResultTest:
        options = (options if options else [selectinload(ResultTest.test)])
        result: ResultTest = (await self.session.execute(select(ResultTest)
                                                         .where(ResultTest.id == result_id)
                                                         .options(*options))).unique().scalar()
        if result.user_id != user_id and result.test.creator_id != user_id:
            raise Exception("Нет доступа к данному результату")
        return result

    @staticmethod
    def _get_options_question():
        return [
            selectinload(Test.questions).joinedload(Question.question_choice),
            selectinload(Test.questions).joinedload(Question.question_not_check),
            selectinload(Test.questions).joinedload(Question.question_input_answer),
        ]

    @staticmethod
    def _get_options():
        return [
            selectinload(ResultTest.answers).selectinload(Answer.question).selectinload(Question.pointer_to_answer),
            selectinload(ResultTest.answers).selectinload(Answer.answers_test),
            selectinload(ResultTest.test).selectinload(Test.theory).selectinload(Theory.chapters),
            selectinload(ResultTest.test).selectinload(Test.questions).selectinload(Question.question_choice),
            selectinload(ResultTest.test).selectinload(Test.questions).selectinload(Question.question_input_answer),
            selectinload(ResultTest.test).selectinload(Test.questions).selectinload(Question.question_not_check),
        ]
