#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os.path
from typing import List

import aspose.words as aw

from webapi.InterfacesControllers.BusinessLogicControllers.ITheoryLogic import ITheoryLogic
from webapi.InterfacesControllers.StorageControllers.ITheoryRepository import ITheoryRepository
from webapi.ViewModel import TheoryViewModel, ChapterTheoryViewModel, UserViewModel


class TheoryLogic(ITheoryLogic):
    path_to_chapters = '../chapters_pdfs/'

    async def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        return await self._repository.Create(aTheory)

    async def Update(self, user: UserViewModel, aTheory: TheoryViewModel) -> TheoryViewModel:
        return await self._repository.Update(user, aTheory)

    async def Get(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        return await self._repository.Get(aTheory)

    async def GetAllFromUser(self, user: UserViewModel) -> List[TheoryViewModel]:
        return await self._repository.GetAllFromUser(user)

    async def MergeChaptersToPdf(self, aTheory: TheoryViewModel, aPath=None) -> str:
        if aPath is None:
            aPath = self.path_to_chapters
        theory = await self.Get(aTheory)
        file_name = aPath + theory.id + ".pdf"
        if os.path.exists(file_name):
            return file_name
        documentPdf = aw.Document()
        for chapter_id in theory.chapters:
            documentHtml = aw.Document(ChapterLogic.path_to_chapters + chapter_id + ".html")
            documentPdf.append_document(documentHtml, aw.ImportFormatMode.KEEP_SOURCE_FORMATTING)
        documentPdf.save(file_name)
        return file_name

    def __init__(self):
        self._repository: ITheoryRepository = ITheoryRepository.__subclasses__()[-1]()
