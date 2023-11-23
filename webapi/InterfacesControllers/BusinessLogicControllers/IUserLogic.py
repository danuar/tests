#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import UserViewModel


class IUserLogic(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def RegisterOrAuthorize(self, aUser: UserViewModel) -> UserViewModel:
        pass

    @abstractmethod
    def Get(self, aUser: UserViewModel) -> UserViewModel:
        pass
