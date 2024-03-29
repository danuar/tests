#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid

import aiofiles
from classy_fastapi import post, put, get, delete
from fastapi import Depends, UploadFile, File
from fastapi.responses import FileResponse

from webapi.InterfacesControllers import IChapterLogic
from webapi.SchemasModel import ChapterTheoryUpdateSchema, ChapterTheorySchema
from webapi.ViewModel import ChapterTheoryViewModel, TheoryViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user, get_chapter_logic, get_async_session


class ChapterController(AbstractController):
    @post("/chapterTheory")
    async def create_chapter_theory(self, chapter_theory: ChapterTheorySchema,
                                    user=Depends(get_user),
                                    logic=Depends(get_chapter_logic)) -> ChapterTheoryViewModel:
        if isinstance(chapter_theory.theory, TheoryViewModel):
            theory = chapter_theory.theory
            theory = TheoryViewModel.Create(theory.name, user, aStudyTime=theory.study_time)
        else:
            theory = TheoryViewModel.GetFromId(chapter_theory.theory)
        return await logic.Create(ChapterTheoryViewModel.Create(chapter_theory.name, theory)
                                  .SetContent(chapter_theory.content))

    @put("/chapterTheory")
    async def update_chapter_theory(self, aId: uuid.UUID, chapter_theory: ChapterTheoryUpdateSchema,
                                    user=Depends(get_user),
                                    logic=Depends(get_chapter_logic)) -> ChapterTheoryViewModel:
        return await logic.Update(user, ChapterTheoryViewModel.Update(aId, chapter_theory.name))

    @get("/chapterTheory")
    async def get_chapter_theory_by_id(self, aId: uuid.UUID,
                                       logic=Depends(get_chapter_logic)) -> ChapterTheoryViewModel:
        return await logic.Get(ChapterTheoryViewModel.Get(aId))

    @delete("/chapterTheory")
    async def delete_chapter_theory_by_id(self, aId: uuid.UUID, user=Depends(get_user),
                                          logic=Depends(get_chapter_logic)) -> ChapterTheoryViewModel:
        return await logic.Delete(ChapterTheoryViewModel.Delete(aId, user.id))

    @get("/chapter_html/{id}", response_class=FileResponse)
    async def get_content_chapter_by_id_in_format_html_document(self, id_: uuid.UUID,
                                                                logic=Depends(get_chapter_logic)):
        path = (await logic.GetContentByChapter(ChapterTheoryViewModel.Get(id_)))[0]
        return FileResponse(path, media_type="multipart/form-data")

    @post("/load_chapter/{id}")
    async def load_content_chapter_by_id(self, id_: uuid.UUID, file: UploadFile = File(media_type="text/html"),
                                         overwrite: bool = True,
                                         logic=Depends(get_chapter_logic)):
        chapter = await logic.LoadChapter(ChapterTheoryViewModel.Get(id_), overwrite, delegate_write=True)
        async with aiofiles.open(chapter.content, 'wb', encoding='utf-8') as out_file:
            while content := await file.read(1024):  # async read chunk
                await out_file.write(content)
        chapter.content = None
        return chapter
