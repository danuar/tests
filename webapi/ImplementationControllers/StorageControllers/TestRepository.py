#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from sqlalchemy import update, select
from sqlalchemy.engine import Result

from webapi.InterfacesControllers import ITestRepository, ICachedService, IUserRepository
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import UserViewModel, TestViewModel
from webapi.db import DbSession, Test, ResultTest


class TestRepository(ITestRepository, AbstractDbRepository):

    def __init__(self):
        super().__init__()
        self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]()
        self.user_repository: IUserRepository = IUserRepository.__subclasses__()[-1]()
        self.session = DbSession().async_session

    async def Create(self, aTest: TestViewModel) -> TestViewModel:
        aTest.CanBeCreated().raiseValidateException()
        test: Test = Test.CreateFrom(aTest)
        if aTest.theory.id is not None:  # Не создаем новую теорию а связываем с существующей
            delattr(test, "theory")
            test.theory_id = aTest.theory.id
        self.session.add(test)
        await self.session.commit()

        return (await self.session.get(Test, test.id)).GetViewModel()

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
        result: Result = (await self.session.execute(select(Test).where(Test.creator_id == aUser.id)))
        return [i.GetViewModel(load_user=False) for i in result.unique().scalars()]

    async def GetCompleted(self, aUser: UserViewModel) -> List[TestViewModel]:
        # todo создать отдельный связь для добавленных тестов у пользователя
        result: Result = (await self.session.execute(select(ResultTest).where(ResultTest.user_id == aUser.id)))
        return [i.test.GetViewModel(load_user=False) for i in result.unique().scalars()]

    async def Get(self, aTest: TestViewModel) -> TestViewModel:
        aTest.CanBeFind().raiseValidateException()
        return (await self.session.get(Test, aTest.id)).GetViewModel(load_user=False)

    async def GetAvailableCountAttempts(self, aUser: UserViewModel, aTest: TestViewModel) -> int:
        test: Test = await self.Get(aTest)
        if test.count_attempts is None:
            return None
        if aUser.tests is None:
            aUser = await self.user_repository.RegisterOrAuthorize(aUser)
        return test.count_attempts - len([i for i in aUser.resultsTests if i.test.id == aTest.id])
