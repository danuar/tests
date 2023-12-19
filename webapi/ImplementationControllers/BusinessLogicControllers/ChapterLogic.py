#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os.path
from typing import List, Union

import aiofiles

from webapi.InterfacesControllers import *
from webapi.ViewModel import ChapterTheoryViewModel, TheoryViewModel


class ChapterLogic(IChapterLogic):
    path_to_chapters = '../chapters/'

    def get_content_filename(self, chapter_id):
        return f"{self.path_to_chapters}{chapter_id}.html"

    async def SaveContentInFile(self, aChapter: ChapterTheoryViewModel):
        assert aChapter is not None
        async with aiofiles.open(self.get_content_filename(aChapter.id), 'w') as out_file:
            await out_file.write(aChapter.content)

    async def GetContentByChapter(self, aChapter: ChapterTheoryViewModel, get_path_to_file=True) -> (
            Union)[list[str], list[ChapterTheoryViewModel]]:
        ids = [aChapter.id] if aChapter.id else []
        if aChapter.theory and aChapter.theory.id:
            theory = await self._theory_repository.Get(TheoryViewModel.GetFromId(aChapter.theory.id))
            ids.extend(i.id for i in theory.chapters)
        if get_path_to_file:
            return [self.path_to_chapters + str(i) + ".html" for i in ids]
        else:
            chapters_with_content = []
            for i in ids:
                if not os.path.exists(self.get_content_filename(i)):
                    chapters_with_content.append(aChapter.Get(i).SetContent(""))
                    continue
                async with aiofiles.open(self.get_content_filename(i), encoding='utf-8') as f:
                    chapters_with_content.append(aChapter.Get(i).SetContent(await f.read()))
            return chapters_with_content

    async def Create(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        return await self._repository.Create(aChapter)

    async def Update(self, aUser, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        return await self._repository.Update(aUser, aChapter)

    async def Get(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        return await self._repository.Get(aChapter)

    async def Delete(self, aChapter: ChapterTheoryViewModel) -> ChapterTheoryViewModel:
        return await self._repository.Delete(aChapter)

    async def LoadChapter(self, aChapter: ChapterTheoryViewModel, overwrite=True, delegate_write=False) -> ChapterTheoryViewModel:
        chapter = await self._repository.Get(aChapter)
        if aChapter.content == "" and delegate_write is False:
            raise Exception("Необходимо добавить контент в главу перед загрузкой")
        if overwrite is False and os.path.exists(f"chapters/{aChapter.id}"):
            raise Exception("Файл главы теории уже добавлен, чтобы перезаписать установите overwrite=True")
        if delegate_write:
            chapter.content = f"{self.path_to_chapters}{aChapter.id}.html"
            return chapter
        await self.SaveContentInFile(chapter)
        return chapter

    def __init__(self):
        self._repository: IChapterRepository = IChapterRepository.__subclasses__()[-1]()
        self._theory_repository: ITheoryRepository = ITheoryRepository.__subclasses__()[-1]()
