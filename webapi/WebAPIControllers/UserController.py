#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipaddress
from pprint import pprint
from typing import List, Annotated, Optional, Union

from classy_fastapi import Routable, get, post
from fastapi import Request, Header, Cookie, Response, Depends

from webapi.InterfacesControllers.BusinessLogicControllers.IUserLogic import IUserLogic
from webapi.SchemasModel import UserSchema
from webapi.ViewModel import UserViewModel
from .AbstractController import AbstractController
from .DefineDepends import get_user


class UserController(AbstractController):

    @post("/")
    async def Authorize(self, user=Depends(get_user)) -> UserSchema:
        return user

    def __init__(self):
        super().__init__()
        self._logic: IUserLogic = IUserLogic.__subclasses__()[-1]()
