#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from sqlalchemy import update

from webapi.InterfacesControllers import ICachedService
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.InterfacesControllers.StorageControllers.IChapterRepository import IChapterRepository
from webapi.ViewModel import ChapterTheoryViewModel, UserViewModel
from webapi.db import DbSession, ChapterTheory


class ChapterRepository(IChapterRepository, AbstractDbRepository):

    def __init__(self):
        super().__init__()
        self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]()
        self.session = DbSession().async_session

    async def Create(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        aChapter.CanBeCreated().raiseValidateException()
        chapter: ChapterTheory = ChapterTheory.CreateFrom(aChapter)
        if aChapter.theory.id is not None:  # Не создаем новую теорию а связываем с существующей
            delattr(chapter, "theory")
            chapter.theory_id = aChapter.theory.id
        self.session.add(chapter)
        await self.session.commit()

        aChapter.id = chapter.id
        return aChapter

    async def Update(self, user: UserViewModel, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        aChapter.CanBeUpdated().raiseValidateException()

        await self.session.execute(update(ChapterTheory)
                                   .where(ChapterTheory.id == aChapter.id)
                                   .values(name=aChapter.name))
        chapter = await self.session.get(ChapterTheory, aChapter.id)
        await self._validate_chapter(chapter, user.id)
        await self.session.commit()

        return chapter.GetViewModel()

    async def Get(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        aChapter.CanBeFind().raiseValidateException()
        return (await self.session.get(ChapterTheory, aChapter.id)).GetViewModel()

    async def Delete(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        aChapter.CanBeDeleted().raiseValidateException()
        chapter = (await self.session.get(ChapterTheory, aChapter.id))
        await self._validate_chapter(chapter, aChapter.theory.creator.id)
        await self.session.delete(chapter)
        await self.session.commit()
        return chapter.GetViewModel()

    async def _validate_chapter(self, chapter: ChapterTheory, user_id):
        if chapter is None:
            raise Exception("Неверно задан id для главы теории")
        if chapter.theory.creator_id != user_id:
            await self.session.rollback()
            raise Exception("Менять теорию может только ее владелец")
