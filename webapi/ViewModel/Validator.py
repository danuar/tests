#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List, Optional


class Validator(object):
    def __init__(self, aEntityType: type, aFieldName: str, aMessage: Optional[str]):
        self.entityType: type = aEntityType
        self.fieldName: str = aFieldName
        self.message: str = aMessage

    def raiseValidateException(self):
        if self.message is not None:
            raise Exception(f"{self.entityType=} {self.fieldName=} {self.message=}")
        return self

    @staticmethod
    def default():
        return Validator(None, None, None)
