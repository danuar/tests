#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod

from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import UserViewModel


class IUserRepository(AbstractDbRepository):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def RegisterOrAuthorize(self, aUser: UserViewModel) -> UserViewModel:
        pass

    @abstractmethod
    async def Get(self, aUser: UserViewModel) -> UserViewModel:
        pass

    @abstractmethod
    async def GetFromSessionToken(self, aToken: str) -> UserViewModel:
        pass
