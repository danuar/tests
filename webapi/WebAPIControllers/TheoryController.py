#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
from typing import List

import aiofiles
from classy_fastapi import post, get, put, delete
from fastapi import Depends
from fastapi.responses import FileResponse

from webapi.ImplementationControllers import ChapterLogic
from webapi.InterfacesControllers import ITheoryLogic, IChapterLogic
from webapi.SchemasModel import TheorySchema
from webapi.ViewModel import TheoryViewModel, ChapterTheoryViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user


class TheoryController(AbstractController):
    @post("/theory")
    async def create_new_theory(self, theory: TheorySchema, user=Depends(get_user)) -> TheoryViewModel:
        return await self._logic.Create(theory.GetViewModel().SetCreator(user))

    @put("/theory")
    async def update_theory_by_id(self, aId: uuid.UUID, theory: TheorySchema, user=Depends(get_user)) -> TheoryViewModel:
        return await self._logic.Update(user, TheoryViewModel.Update(aId, theory.name, theory.studyTime))

    @get("/theory")
    async def get_theory_by_id(self, aId: uuid.UUID) -> TheoryViewModel:
        return await self._logic.Get(TheoryViewModel.GetFromId(aId))

    @get("/pdf")
    async def get_theory_in_format_pdf(self, aId: uuid.UUID):
        return FileResponse(self._logic.MergeChaptersToPdf(TheoryViewModel.GetFromId(aId), ChapterLogic.path_to_chapters), media_type="multipart/pdf")
        # todo pdf + загрузка по атрибуту content + прохождение теста + графики

    @get("/chapters_html")
    async def get_chapters_in_format_list_html_documents(self, aId: uuid.UUID):
        paths = await self._chapter_logic.GetContentByChapter(
            ChapterTheoryViewModel.Create(None, TheoryViewModel.GetFromId(aId)))
        return [FileResponse(path, media_type="multipart/form-data") for path in paths]

    @get("/theories")
    async def get_created_theories(self, user=Depends(get_user)) -> List[TheoryViewModel]:
        return await self._logic.GetAllFromUser(user)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logic: ITheoryLogic = ITheoryLogic.__subclasses__()[-1]()
        self._chapter_logic: IChapterLogic = IChapterLogic.__subclasses__()[-1]()
