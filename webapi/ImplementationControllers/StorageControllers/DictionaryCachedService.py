#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime

from typing import List

import jsonpickle

from webapi.InterfacesControllers.StorageControllers.ICachedService import ICachedService


class DictionaryCachedService(ICachedService):
    def Remove(self, aKey: str):
        if aKey not in self.cache:
            self.result_last_operation = False
            return
        self.cache.pop(aKey)

    __lifeTimeCache = datetime.timedelta(minutes=30)
    cache: dict[str, tuple[datetime.datetime, object]] = {}

    def __init__(self):
        super().__init__()
        self.result_last_operation: bool = False

    def Get(self, aKey: str) -> object:
        value = self.cache[aKey]
        if datetime.datetime.now() > value[0] + self.__lifeTimeCache:
            raise KeyError(f"Timeout cache {aKey=} {value=}")
        return value[1]

    def Set(self, aKey: str, aValue: object) -> bool:
        self.cache[aKey] = (datetime.datetime.now(), aValue)
        return True

    def TryGet(self, aKey: str) -> object:
        self.result_last_operation = True
        try:
            return self.Get(aKey)
        except KeyError:
            self.result_last_operation = False

    def cache_decorate(self, func, skip_first_elemnt=True):
        async def wrapper(*args, **kwargs):
            serialize_args = args[1:] if skip_first_elemnt else args
            key = f"{func.__name__}/{jsonpickle.encode(serialize_args)}{jsonpickle.encode(kwargs)}"
            result = self.TryGet(key)
            if self.result_last_operation:
                return result
            result = await func(*args, **kwargs)
            self.Set(key, result)
            return result
        return wrapper
