#!/usr/bin/python
# -*- coding: UTF-8 -*-
import asyncio
import datetime
import difflib
from threading import Timer
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSessionTransaction
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.sql.base import Options

from webapi.InterfacesControllers import IResultTestRepository, ICachedService
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import ResultTestViewModel, UserViewModel, TestViewModel
from webapi.db import DbSession, ResultTest, Test, Question, Answer


class ResultTestRepository(IResultTestRepository, AbstractDbRepository):

    def __init__(self):
        super().__init__()
        self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]()
        self.session = DbSession().async_session

    async def Create(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        result = ResultTest.CreateFrom(aResult)
        self.session.add(result)

        await self.session.commit()
        result.test = await self.session.get(Test, result.test_id, [
            joinedload(Test.questions).joinedload(Question.question_choice),
            joinedload(Test.questions).joinedload(Question.question_not_check),
            joinedload(Test.questions).joinedload(Question.question_input_answer),
        ])
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

    async def Update(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        result_db = await self._get(aUser.id, aResult.id, [
            joinedload(ResultTest.test).joinedload(Test.questions),
            joinedload(ResultTest.answers)
        ])
        if result_db.completed_date:
            raise Exception("Нельзя изменить результаты уже пройденного теста")
        test = result_db.test
        questions_db = (await self.session.execute(select(Question)
                                                   .where(Question.id in [i.id for i in test.questions])
                                                   .options(joinedload(Question.question_input_answer),
                                                            joinedload(Question.question_choice),
                                                            joinedload(Question.question_not_check)))
                        ).unique().scalars()
        questions = {i.id: i for i in questions_db}
        answers = {i.id: i for i in result_db.answers}
        for answer in aResult.answers:
            answer.mark = 0
            if answer.id in answers:
                raise Exception("Ответ на вопрос уже добавлен")
            if answer.question.id not in questions:
                raise Exception("В тесте нет вопроса на который добавляется ответ")
            question = questions[answer.question.id]
            if test.completion_time is None and answer.complitionTime > question.complition_time:
                continue  # Превышено время ответа на вопрос
            if question.question_input_answer:
                ratio = question.question_input_answer.k_misspell
                result_ratio = difflib.SequenceMatcher(None, answer.answer,
                                                       question.question_input_answer.correct_answer, True).ratio()
                if result_ratio > ratio:
                    answer.mark = question.weight
            elif question.question_choice:
                corrects = {i.id: i for i in question.question_choice.answers_test}
                count_correct = sum(1 if i.id in corrects else -1 for i in answer.answers_test)
                if count_correct > 0:
                    answer.mark = count_correct * question.weight // len(corrects)
        result_db.note = aResult.note
        result_db.completed_date = aResult.completedDate
        result_db.answers.extend(Answer.CreateFrom(answer) for answer in aResult.answers)
        await self.session.commit()

        return result_db.GetViewModel()

    async def Get(self, aUser: UserViewModel, aResult: ResultTestViewModel) -> ResultTestViewModel:
        return (await self._get(aUser.id, aResult.id)).GetViewModel()

    async def GetFromUser(self, aUser: UserViewModel) -> List[ResultTestViewModel]:
        result = await self.session.execute(select(ResultTest).where(ResultTest.user_id == aUser.id))
        return [i.GetViewModel() for i in result.unique().scalars()]

    async def GetFromTest(self, aUser: UserViewModel, aTest: TestViewModel) -> List[ResultTestViewModel]:
        test: Test = await self.session.get(Test, aTest.id, options=[joinedload(Test.results_tests)])
        if test.creator_id != aUser.id:
            raise Exception("Только создатель теста может получить результаты теста")
        return [i.GetViewModel() for i in test.results_tests]

    async def _get(self, user_id, result_id, options: Optional[list[Options]] = None) -> ResultTest:
        options = (options if options else [])
        result: ResultTest = await self.session.get(ResultTest, result_id, options=options)
        if result.user_id != user_id and result.test.creator_id != user_id:
            raise Exception("Нет доступа к данному результату")
        return result
