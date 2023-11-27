#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid

from typing import List

from classy_fastapi import post, put, get
from fastapi import Depends

from webapi.InterfacesControllers import ITestLogic
from webapi.SchemasModel import TestSchema, TestUpdateSchema
from webapi.ViewModel import TestViewModel, TheoryViewModel, ChapterTheoryViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user


class TestController(AbstractController):

    @post("/test")
    async def create_new_test(self, test: TestSchema, user=Depends(get_user)) -> TestViewModel:
        if isinstance(test.theory, TheoryViewModel):
            theory = test.theory
            theory = (TheoryViewModel
                      .Create(theory.name, user, aStudyTime=theory.studyTime,
                              chapters=[ChapterTheoryViewModel.Create(i.name, None) for i in theory.chapters]))
        else:
            theory = TheoryViewModel.GetFromId(test.theory)
        return await self._logic.Create(TestViewModel.Create(test.name, test.count_attempts, test.shuffle,
                                                             test.show_answer, user, theory, test.complition_time))

    @put("/test")
    async def update_own_test(self, aId: uuid.UUID, aTest: TestUpdateSchema, user=Depends(get_user)) -> TestViewModel:
        return await self._logic.Update(user, TestViewModel.Update(aId, aTest.name))

    @get("/created_test")
    async def get_created_test(self, user=Depends(get_user)) -> List[TestViewModel]:
        return await self._logic.GetCreated(user)

    @get("/comleted_test")
    async def get_completed_test(self, user=Depends(get_user)) -> List[TestViewModel]:
        return await self._logic.GetCompleted(user)

    @get("/test")
    async def get_test_by_id(self, aId: uuid.UUID) -> TestViewModel:
        return await self._logic.Get(TestViewModel.GetFromId(aId))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logic: ITestLogic = ITestLogic.__subclasses__()[-1]()
