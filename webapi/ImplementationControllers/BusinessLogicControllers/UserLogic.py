#!/usr/bin/python
# -*- coding: UTF-8 -*-

from webapi.InterfacesControllers.BusinessLogicControllers.IUserLogic import IUserLogic
from webapi.InterfacesControllers.StorageControllers.IUserRepository import IUserRepository
from webapi.ViewModel import UserViewModel


class UserLogic(IUserLogic):
    async def Get(self, aUser: UserViewModel) -> UserViewModel:
        return await self._repository.Get(aUser)

    async def RegisterOrAuthorize(self, aUser: UserViewModel) -> UserViewModel:
        return await self._repository.RegisterOrAuthorize(aUser)

    async def GetFromSession(self, aToken: str) -> UserViewModel:
        return await self._repository.GetFromSessionToken(aToken)

    def __init__(self):
        self._repository: IUserRepository = IUserRepository.__subclasses__()[-1]()
