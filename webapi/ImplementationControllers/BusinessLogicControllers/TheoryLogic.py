#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import os.path
from typing import List

import aspose.words as aw

from webapi.InterfacesControllers import IChapterLogic
from webapi.InterfacesControllers.BusinessLogicControllers.ITheoryLogic import ITheoryLogic
from webapi.InterfacesControllers.StorageControllers.ITheoryRepository import ITheoryRepository
from webapi.ViewModel import TheoryViewModel, UserViewModel


class TheoryLogic(ITheoryLogic):
    path_to_chapters_pdf = '../chapters_pdfs/'
    path_to_chapters_html = '../chapters/'

    async def Create(self, aTheory: TheoryViewModel) -> TheoryViewModel:
        theory = await self._repository.Create(aTheory)
        for chapter in (i for i in theory.chapters if i.content is not None and i.content != ""):
            await self.chapter_logic.SaveContentInFile(chapter)
        return theory

    async def Update(self, user: UserViewModel, aTheory: TheoryViewModel) -> TheoryViewModel:
        return await self._repository.Update(user, aTheory)

    async def Get(self, aTheory: TheoryViewModel, get_content: bool) -> TheoryViewModel:
        theory = await self._repository.Get(aTheory)
        if not get_content:
            return theory
        for chapter in theory.chapters:
            chapter.content = (await self.chapter_logic.GetContentByChapter(chapter, False))[0].content
        return theory

    async def GetAllFromUser(self, user: UserViewModel, get_content: bool) -> List[TheoryViewModel]:
        theories = await self._repository.GetAllFromUser(user)
        if not get_content:
            return theories
        for theory in theories:
            for chapter in theory.chapters:
                chapter.content = (await self.chapter_logic.GetContentByChapter(chapter, False))[0].content
        return theories

    async def MergeChaptersToPdf(self, aTheory: TheoryViewModel, aPath=None) -> str:
        if aPath is None:
            aPath = self.path_to_chapters_pdf
        theory = await self.Get(aTheory)
        file_name = f"{aPath}{theory.id}.pdf"
        if os.path.exists(file_name):
            return file_name
        documentPdf = aw.Document()
        for path in (f"{self.path_to_chapters_html}{i.id}.html" for i in theory.chapters):
            if not os.path.exists(path):
                logging.warning(f"У главы теории{theory} не существует html документа по пути {path}")
                continue
            documentHtml = aw.Document(path)
            documentPdf.append_document(documentHtml, aw.ImportFormatMode.KEEP_SOURCE_FORMATTING)
        documentPdf.save(file_name)
        return file_name

    def __init__(self):
        self._repository: ITheoryRepository = ITheoryRepository.__subclasses__()[-1]()
        self.chapter_logic = IChapterLogic.__subclasses__()[-1]()
