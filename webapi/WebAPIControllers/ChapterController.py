#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
from typing import List

from classy_fastapi import post, put, get, delete
from fastapi import Depends

from webapi.InterfacesControllers import IChapterLogic
from webapi.SchemasModel import ChapterTheoryUpdateSchema, ChapterTheorySchema
from webapi.ViewModel import ChapterTheoryViewModel, TheoryViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user


class ChapterController(AbstractController):
    @post("/chapterTheory")
    async def create_chapter_theory(self, chapter_theory: ChapterTheorySchema,
                                    user=Depends(get_user)) -> ChapterTheoryViewModel:
        if isinstance(chapter_theory.theory, TheoryViewModel):
            theory = chapter_theory.theory
            theory = TheoryViewModel.Create(theory.name, user, aStudyTime=theory.studyTime)
        else:
            theory = TheoryViewModel.GetFromId(chapter_theory.theory)
        return await self._logic.Create(ChapterTheoryViewModel.Create(chapter_theory.name, theory))

    @put("/chapterTheory")
    async def update_chapter_theory(self, aId: uuid.UUID, chapter_theory: ChapterTheoryUpdateSchema,
                                    user=Depends(get_user)) -> ChapterTheoryViewModel:
        return await self._logic.Update(user, ChapterTheoryViewModel.Update(aId, chapter_theory.name))

    @get("/chapterTheory")
    async def get_chapter_theory_by_id(self, aId: uuid.UUID) -> ChapterTheoryViewModel:
        return await self._logic.Get(ChapterTheoryViewModel.Get(aId))

    @delete("/chapterTheory")
    async def delete_chapter_theory_by_id(self, aId: uuid.UUID, user=Depends(get_user)) -> ChapterTheoryViewModel:
        return await self._logic.Delete(ChapterTheoryViewModel.Delete(aId, user.id))

    async def get_content_chapter_by_id_in_format_html_document(self, aId: int):
        pass

    def __init__(self):
        super().__init__()
        self._logic: IChapterLogic = IChapterLogic.__subclasses__()[-1]()
