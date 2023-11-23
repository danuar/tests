#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from classy_fastapi import Routable, get

from webapi.InterfacesControllers.BusinessLogicControllers.IUserLogic import IUserLogic
from webapi.ViewModel import UserViewModel


class UserController(Routable):

    @get("/")
    def Authorize(self, aUser: UserViewModel) -> UserViewModel:
        result = self._logic.RegisterOrAuthorize(aUser)

        return result

    def __init__(self, userLogic: IUserLogic):
        super().__init__()
        self._logic: IUserLogic = userLogic
