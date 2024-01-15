#!/usr/bin/python
# -*- coding: UTF-8 -*-
from operator import and_, or_
from typing import List

from sqlalchemy import update, select, func
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload, selectinload

from webapi.InterfacesControllers import ITestRepository, ICachedService, IUserRepository
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import UserViewModel, TestViewModel
from webapi.db import DbSession, Test, ResultTest, Question, QuestionChoice, Theory

_cached_service: ICachedService = ICachedService.__subclasses__()[-1]()


class TestRepository(ITestRepository):

    async def GetAvailableTests(self, aUser):
        result: Result = (await self.session.execute(select(Test)
                                                     .where(or_(ResultTest.user_id == aUser.id, Test.creator_id == aUser.id))
                                                     .options(*self.get_options(), selectinload(Test.results_tests))))
        return [i.GetViewModel(load_user=False) for i in result.unique().scalars()]

    async def Create(self, aTest: TestViewModel) -> TestViewModel:
        aTest.CanBeCreated().raiseValidateException()
        test: Test = Test.CreateFrom(aTest)
        if aTest.theory.id is not None:  # Не создаем новую теорию а связываем с существующей
            delattr(test, "theory")
            test.theory_id = aTest.theory.id
        self.session.add(test)
        await self.session.commit()

        return (await self.session.get(Test, test.id, options=self.get_options())).GetViewModel(load_user=False)

    async def Update(self, aUser: UserViewModel, aTest: TestViewModel) -> TestViewModel:
        aTest.CanBeUpdated().raiseValidateException()

        await self.session.execute(update(Test)
                                   .where(Test.id == aTest.id)
                                   .values(name=aTest.name))
        test = await self.session.get(Test, aTest.id)
        if test is None:
            raise Exception("Неверно задан id для теста")
        if test.creator_id != test.id:
            await self.session.rollback()
            raise Exception("Менять тест может только его владелец")
        await self.session.commit()
        return test.GetViewModel(load_user=False)

    async def GetCreated(self, aUser: UserViewModel) -> List[TestViewModel]:
        result: Result = (await self.session.execute(select(Test)
                                                     .where(Test.creator_id == aUser.id)
                                                     .options(*self.get_options())))
        return [i.GetViewModel(load_user=False) for i in result.unique().scalars()]

    @_cached_service.cache_decorate
    async def GetCompleted(self, aUser: UserViewModel) -> List[TestViewModel]:
        result: Result = (await self.session.execute(select(Test)
                                                     .where(ResultTest.user_id == aUser.id)
                                                     .options(*self.get_options(), selectinload(Test.results_tests))))
        return [i.GetViewModel(load_user=False) for i in result.unique().scalars()]

    async def Get(self, aTest: TestViewModel) -> TestViewModel:
        aTest.CanBeFind().raiseValidateException()
        options = self.get_options() + [joinedload(Test.theory).joinedload(Theory.chapters)]
        test: Test = await self.session.get(Test, aTest.id, options=options)
        if test is None:
            raise Exception(f"Not find test by {aTest.id=}")
        return test.GetViewModel(load_user=False)

    async def GetAvailableCountAttempts(self, aUser: UserViewModel, aTest: TestViewModel) -> int:
        test: TestViewModel = await self.Get(aTest)
        if test.count_attempts is None:
            return None
        count = await self.session.scalar(select(func.count(ResultTest.id)).where(
            and_(ResultTest.test_id == test.id, ResultTest.user_id == aUser.id)))
        return test.count_attempts - count

    @staticmethod
    def get_options():
        return [
            selectinload(Test.questions).selectinload(Question.question_choice).joinedload(QuestionChoice.answers_test),
            selectinload(Test.questions).selectinload(Question.question_input_answer),
            selectinload(Test.questions).selectinload(Question.question_not_check),
            joinedload(Test.theory)]
