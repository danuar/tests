#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import uuid
import zipfile
from io import BytesIO
from typing import List

from classy_fastapi import post, get, put
from fastapi import Depends
from fastapi.responses import FileResponse
from starlette.responses import StreamingResponse

from webapi.InterfacesControllers import ITheoryLogic, IChapterLogic
from webapi.SchemasModel import TheorySchema
from webapi.SchemasModel.ResponseModels import *
from webapi.ViewModel import TheoryViewModel, ChapterTheoryViewModel
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.WebAPIControllers.DefineDepends import get_user, get_theory_logic, get_chapter_logic


class TheoryController(AbstractController):
    @post("/theory")
    async def create_new_theory(self, theory: TheorySchema, user=Depends(get_user),
                                logic=Depends(get_theory_logic)) -> TheoryResponseSchema:
        return await logic.Create(theory.GetViewModel().SetCreator(user))

    @put("/theory")
    async def update_theory_by_id(self, aId: uuid.UUID, theory: TheorySchema, user=Depends(get_user),
                                  logic=Depends(get_theory_logic)) -> TheoryResponseSchema:
        return await logic.Update(user, TheoryViewModel.Update(aId, theory.name, theory.study_time).AddChapters(
            *[ChapterTheoryViewModel.Create(i.name, None).SetContent(i.content) for i in theory.chapters]
        ))

    @get("/theory")
    async def get_theory_by_id(self, aId: uuid.UUID, get_content: bool = False,
                               logic=Depends(get_theory_logic)) -> TheoryResponseSchema:
        return await logic.Get(TheoryViewModel.GetFromId(aId), get_content)

    @get("/pdf")
    async def get_theory_in_format_pdf(self, aId: uuid.UUID,
                                       logic=Depends(get_theory_logic)):
        return FileResponse(await logic.MergeChaptersToPdf(TheoryViewModel.GetFromId(aId)),
                            filename=f"theory.pdf", media_type="multipart/octet-stream")

    @get("/chapters_html")
    async def get_chapters_in_format_zip_list_html_documents(self, aId: uuid.UUID,
                                                             logic=Depends(get_chapter_logic)):
        paths = await logic.GetContentByChapter(ChapterTheoryViewModel.Create(None, TheoryViewModel.GetFromId(aId)))
        zip_io = BytesIO()
        with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as temp_zip:
            for fpath in [os.path.abspath(p) for p in paths if os.path.exists(p)]:
                temp_zip.write(fpath, os.path.join("/chapters/", os.path.split(fpath)[1]))
        return StreamingResponse(
            iter(zip_io.getvalue()), media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment; filename=chapters.zip"}
        )

    @get("/theories")
    async def get_created_theories(self, get_content: bool = False, user=Depends(get_user),
                                   logic=Depends(get_theory_logic)) -> List[TheoryResponseSchema]:
        return await logic.GetAllFromUser(user, get_content)
