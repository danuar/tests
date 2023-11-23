#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime

from typing import List

from webapi.InterfacesControllers.StorageControllers.ICachedService import ICachedService


class DictionaryCachedService(ICachedService):
    __lifeTimeCache = datetime.timedelta(minutes=30)
    cache: dict[str, tuple[datetime.datetime, object]] = {}

    def __init__(self):
        self.result_last_operation: bool = None

    def Get(self, aKey: str) -> object:
        value = self.cache[aKey]
        if datetime.datetime.now() > value[0]:
            raise Exception(f"Timeout cache {aKey=} {value=}")
        return value[1]

    def Set(self, aKey: str, aValue: object) -> bool:
        self.cache[aKey] = (datetime.datetime.now(), aValue)

    def TryGet(self, aKey: str) -> object:
        self.result_last_operation = True
        try:
            return self.Get(aKey)
        except Exception:
            self.result_last_operation = False
