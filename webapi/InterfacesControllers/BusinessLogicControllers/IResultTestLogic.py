#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from webapi.ViewModel import ResultTestViewModel, UserViewModel


class IResultTestLogic(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    @abstractmethod
    async def Create(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    @abstractmethod
    async def Update(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    @abstractmethod
    async def Get(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass

    @abstractmethod
    async def GetFromUser(self, aUser: UserViewModel) -> List[ResultTestViewModel]:
        pass

    @abstractmethod
    async def CompleteTest(self, aResult: ResultTestViewModel) -> ResultTestViewModel:
        pass