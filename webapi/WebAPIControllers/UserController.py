#!/usr/bin/python
# -*- coding: UTF-8 -*-
import ipaddress
from pprint import pprint
from typing import List, Annotated, Optional

from classy_fastapi import Routable, get, post
from fastapi import Request, Header

from webapi.InterfacesControllers.BusinessLogicControllers.IUserLogic import IUserLogic
from webapi.SchemasModel import UserSchema
from webapi.ViewModel import UserViewModel
from .AbstractController import AbstractController


class UserController(AbstractController):

    @post("/")
    async def Authorize(self, user_agent: str, request: Request) -> UserSchema:
        int_ipaddress = int(ipaddress.ip_address(request.client.host))
        result = await self._logic.RegisterOrAuthorize(UserViewModel.Create(int_ipaddress, user_agent))

        return result

    def __init__(self):
        super().__init__()
        self._logic: IUserLogic = IUserLogic.__subclasses__()[-1]()
