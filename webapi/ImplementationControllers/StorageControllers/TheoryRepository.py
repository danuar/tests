#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from sqlalchemy import update, select
from sqlalchemy.engine import Result

from webapi.InterfacesControllers import ITheoryRepository, ICachedService
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import TheoryViewModel, UserViewModel
from webapi.db import DbSession, Theory


class TheoryRepository(ITheoryRepository, AbstractDbRepository):

    def __init__(self):
        super().__init__()
        self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]()
        self.session = DbSession().async_session

    async def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        aTheory.CanBeCreated().raiseValidateException()
        theory: Theory = Theory.CreateFrom(aTheory)
        self.session.add(theory)
        await self.session.commit()

        # todo пофиксить дрисню
        return TheoryViewModel(theory.id, theory.name, theory.study_time, [], [], aTheory.creator)

    async def Update(self, user: UserViewModel, aTheory: TheoryViewModel) -> TheoryViewModel:
        aTheory.CanBeUpdated().raiseValidateException()

        await self.session.execute(update(Theory)
                                   .where(Theory.id == aTheory.id)
                                   .values(name=aTheory.name, study_time=aTheory.studyTime))
        theory: Theory = await self.session.get(Theory, aTheory.id)
        if theory is None:
            raise Exception("Неверно задан id для теории")
        if theory.creator_id != user.id:
            await self.session.rollback()
            raise Exception("Менять теорию может только ее владелец")
        await self.session.commit()

        return theory.GetViewModel()

    async def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        return (await self.session.get(Theory, aTheory.id)).GetViewModel()

    async def GetAllFromUser(self, user: UserViewModel) -> List[TheoryViewModel]:
        result: Result = (await self.session.execute(select(Theory).where(Theory.creator_id == user.id)))
        return [i.GetViewModel().SetCreator(None) for i in result.unique().scalars()]
