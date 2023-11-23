#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List


class ICachedService(object):
    """@Interface"""
    __metaclass__ = ABCMeta

    def __init__(self):
        self.result_last_operation: bool = None

    @abstractmethod
    def Get(self, aKey: str) -> object:
        pass

    @abstractmethod
    def Set(self, aKey: str, aValue: object) -> bool:
        pass

    @abstractmethod
    def TryGet(self, aKey: str) -> object:
        pass
