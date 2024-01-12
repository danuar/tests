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
from webapi.WebAPIControllers.DefineDepends import get_user


class TheoryController(AbstractController):
    @post("/theory")
    async def create_new_theory(self, theory: TheorySchema, user=Depends(get_user)) -> TheoryResponseSchema:
        return await self._logic.Create(theory.GetViewModel().SetCreator(user))

    @put("/theory")
    async def update_theory_by_id(self, aId: uuid.UUID, theory: TheorySchema, user=Depends(get_user)) -> TheoryResponseSchema:
        return await self._logic.Update(user, TheoryViewModel.Update(aId, theory.name, theory.study_time).AddChapters(
            *[ChapterTheoryViewModel.Create(i.name, None).SetContent(i.content) for i in theory.chapters]
        ))

    @get("/theory")
    async def get_theory_by_id(self, aId: uuid.UUID, get_content: bool = False) -> TheoryResponseSchema:
        return await self._logic.Get(TheoryViewModel.GetFromId(aId), get_content)

    @get("/pdf")
    async def get_theory_in_format_pdf(self, aId: uuid.UUID):
        return FileResponse(await self._logic.MergeChaptersToPdf(TheoryViewModel.GetFromId(aId)),
                            filename=f"theory.pdf", media_type="multipart/octet-stream")

    @get("/chapters_html")
    async def get_chapters_in_format_zip_list_html_documents(self, aId: uuid.UUID):
        paths = await self._chapter_logic.GetContentByChapter(
            ChapterTheoryViewModel.Create(None, TheoryViewModel.GetFromId(aId)))
        zip_io = BytesIO()
        with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as temp_zip:
            for fpath in [os.path.abspath(p) for p in paths if os.path.exists(p)]:
                temp_zip.write(fpath, os.path.join("/chapters/", os.path.split(fpath)[1]))
        return StreamingResponse(
            iter(zip_io.getvalue()),            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment; filename=chapters.zip"}
        )

    @get("/theories")
    async def get_created_theories(self, get_content: bool = False, user=Depends(get_user)) -> List[TheoryResponseSchema]:
        return await self._logic.GetAllFromUser(user, get_content)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logic: ITheoryLogic = ITheoryLogic.__subclasses__()[-1]()
        self._chapter_logic: IChapterLogic = IChapterLogic.__subclasses__()[-1]()
