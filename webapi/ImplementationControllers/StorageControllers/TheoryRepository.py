#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from sqlalchemy import update, select
from sqlalchemy.engine import Result

from webapi.InterfacesControllers import ITheoryRepository, ICachedService
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import TheoryViewModel, UserViewModel
from webapi.db import DbSession, Theory, ChapterTheory


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
        await self.session.refresh(theory, ["chapters"])

        result = theory.GetViewModel(load_user=False)
        for i, chapter in enumerate(result.chapters):
            chapter.SetContent(aTheory.chapters[i].content)
        return result

    async def Update(self, user: UserViewModel, aTheory: TheoryViewModel) -> TheoryViewModel:
        aTheory.CanBeUpdated().raiseValidateException()

        theory: Theory = await self.session.get(Theory, aTheory.id)
        if theory is None:
            raise Exception("Неверно задан id для теории")
        if theory.creator_id != user.id:
            await self.session.rollback()
            raise Exception("Менять теорию может только ее владелец")
        theory.study_time = aTheory.study_time
        theory.name = aTheory.name
        theory.chapters.extend(ChapterTheory.CreateFrom(i) for i in aTheory.chapters)
        await self.session.commit()

        return theory.GetViewModel()

    async def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        return (await self.session.get(Theory, aTheory.id)).GetViewModel()

    async def GetAllFromUser(self, user: UserViewModel) -> List[TheoryViewModel]:
        result: Result = (await self.session.execute(select(Theory).where(Theory.creator_id == user.id)))
        return [i.GetViewModel().SetCreator(user.id) for i in result.unique().scalars()]
