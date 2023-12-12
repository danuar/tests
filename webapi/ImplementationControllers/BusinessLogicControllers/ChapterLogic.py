#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os.path
from typing import List, Union

from webapi.InterfacesControllers import *
from webapi.ViewModel import ChapterTheoryViewModel, TheoryViewModel


class ChapterLogic(IChapterLogic):
    path_to_chapters = '../chapters/'

    async def GetContentByChapter(self, aChapter: ChapterTheoryViewModel, get_path_to_file=True) -> (
            Union)[list[str], list[ChapterTheoryViewModel]]:
        ids = [aChapter.id] if aChapter.id else []
        if aChapter.theory and aChapter.theory.id:
            theory = await self._theory_repository.Get(TheoryViewModel.GetFromId(aChapter.theory.id))
            ids.extend(i.id for i in theory.chapters)
        if get_path_to_file:
            return [self.path_to_chapters + str(i) + ".html" for i in ids]
        else:
            result = []
            for i in ids:
                with open(self.path_to_chapters + str(i) + ".html") as f:
                    result.append(aChapter.Get(i).SetContent(f.read()))
            return result

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
        if overwrite is False and os.path.exists("chapters/" + aChapter.id):
            raise Exception("Файл главы теории уже добавлен, чтобы перезаписать установите overwrite=True")
        if delegate_write:
            chapter.content = self.path_to_chapters + str(aChapter.id) + ".html"
            return chapter
        with open(self.path_to_chapters + str(aChapter.id) + ".html", "w") as f:
            f.write(aChapter.content)
        return chapter

    def __init__(self):
        self._repository: IChapterRepository = IChapterRepository.__subclasses__()[-1]()
        self._theory_repository: ITheoryRepository = ITheoryRepository.__subclasses__()[-1]()
