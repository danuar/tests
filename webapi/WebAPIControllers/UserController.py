#!/usr/bin/python
# -*- coding: UTF-8 -*-

from classy_fastapi import get
from fastapi import Depends

from webapi.InterfacesControllers.BusinessLogicControllers.IUserLogic import IUserLogic
from webapi.SchemasModel import UserSchema
from .AbstractController import AbstractController
from .DefineDepends import get_user, get_async_session
from ..SchemasModel.ResponseModels import UserResponseSchema


class UserController(AbstractController):

    @get("/")
    async def Authorize(self, user=Depends(get_user)) -> UserResponseSchema:
        return user
