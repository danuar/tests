#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import UserViewModel


class IUserRepository(object):
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
