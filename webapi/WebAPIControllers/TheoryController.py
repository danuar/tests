#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
from typing import List

from classy_fastapi import post, get, put, delete
from fastapi import Depends

from webapi.InterfacesControllers import ITheoryLogic
from webapi.SchemasModel import TheorySchema
from webapi.ViewModel import TheoryViewModel
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
        pass

    @get("/chapters_html")
    async def get_chapters_in_format_list_html_documents(self, aId: uuid.UUID):
        pass

    @get("/theories")
    async def get_created_theories(self, user=Depends(get_user)) -> List[TheoryViewModel]:
        return await self._logic.GetAllFromUser(user)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logic: ITheoryLogic = ITheoryLogic.__subclasses__()[-1]()
