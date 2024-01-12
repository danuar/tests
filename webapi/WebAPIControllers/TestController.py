#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
from typing import List

from classy_fastapi import post, put, get
from fastapi import Depends

from webapi.InterfacesControllers import ITestLogic
from webapi.SchemasModel import TestSchema, TestUpdateSchema
from webapi.ViewModel import TestViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user


class TestController(AbstractController):

    @post("/test")
    async def create_new_test(self, test: TestSchema, user=Depends(get_user)) -> TestViewModel:
        return await self._logic.Create(test.GetViewModel().SetCreator(user))

    @put("/test")
    async def update_own_test(self, aId: uuid.UUID, aTest: TestUpdateSchema, user=Depends(get_user)) -> TestViewModel:
        return await self._logic.Update(user, TestViewModel.Update(aId, aTest.name)
                                        .AddQuestions([i.GetViewModel() for i in aTest.questions]))

    @get("/created_test")
    async def get_created_tests(self, user=Depends(get_user)) -> List[TestViewModel]:
        return await self._logic.GetCreated(user)

    @get("/completed_test")
    async def get_completed_tests(self, user=Depends(get_user)) -> List[TestViewModel]:
        return await self._logic.GetCompleted(user)

    @get("/available_test")
    async def get_available_tests(self, user=Depends(get_user)) -> List[TestViewModel]:
        return await self._logic.GetAvailableTests(user)

    @get("/test")
    async def get_test_by_id(self, aId: uuid.UUID) -> TestViewModel:
        return await self._logic.Get(TestViewModel.GetFromId(aId))

    @get("/available_count_attempts")
    async def get_avilable_count_attempts_passing_test_from_current_user(self, test_id: uuid.UUID, user=Depends(get_user)):
        return await self._logic.GetAvailableCountAttempts(user, TestViewModel.GetFromId(test_id))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logic: ITestLogic = ITestLogic.__subclasses__()[-1]()
