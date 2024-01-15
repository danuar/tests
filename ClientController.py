import abc
import datetime
import json
import logging
import sys
import time
import uuid
from typing import Type, Optional, TypeVar

import aiohttp
import jsonpickle
import requests
from dacite import from_dict, Config

from config import API_URL

T = TypeVar("T")


class BaseClientController:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(cls)
        return cls.instance

    def __init__(self, user_agent: Optional[str] = None):
        if self.__class__.instance is not None:
            return
        self.url = API_URL
        self.user_agent = user_agent
        self.ip_address = None
        self.session = requests.session()
        self.__class__.instance = self

    def _parse_value(self, json: dict):
        for key, value in json.items():
            if isinstance(value, str):
                res = self._parse(value, datetime.datetime.fromisoformat)
                res = self._parse(res, datetime.time.fromisoformat)
                res = self._parse(res, uuid.UUID)
                json[key] = res
        return json

    @staticmethod
    def _parse(value: str, func):
        try:
            if value.isdigit(): return value
            value = func(value)
        except:
            pass
        return value

    def _hangle_result(self, res, ResponseType):
        config = Config(check_types=False, )
        if ResponseType is dict:
            return res
        if isinstance(res, list):
            return [from_dict(ResponseType, i, config) for i in res]
        if isinstance(res, dict):
            return from_dict(ResponseType, res, config)
        return ResponseType(res) if res is not None else None


class AsyncHttpClientController(BaseClientController, metaclass=abc.ABCMeta):

    def __init__(self, user_agent: Optional[str] = None):
        super().__init__(user_agent)
        if self.__class__.instance is not None and isinstance(self.session, aiohttp.ClientSession):
            return
        self.session = aiohttp.ClientSession()
        self.__class__.instance = self

    async def get(self, url: str, ResponseType: Type[T], **query_params):
        return await self.request(url, "get", ResponseType, **query_params)

    async def post(self, url: str, request_body: object, ResponseType: Type[T], **query_params):
        return await self.request(url, "post", ResponseType, request_body=request_body, **query_params)

    async def put(self, url: str, request_body: object, ResponseType: Type[T], **query_params):
        return await self.request(url, "put", ResponseType, request_body=request_body, **query_params)

    async def delete(self, url: str, ResponseType: Type[T], **query_params):
        return await self.request(url, "delete", ResponseType, **query_params)

    async def request(self, url: str, method: str, ResponseType: Type[T], *, request_body=None, **query_params):
        try:
            return await self._request(url, method, ResponseType, request_body=request_body, **query_params)
        except:
            await self.handle_exception(sys.exc_info()[0], self.url + url, method, ResponseType, request_body, **query_params)

    async def _request(self, url: str, method: str, ResponseType: Type[T], *, request_body=None, **query_params):
        if self.user_agent is not None:
            query_params['user_agent'] = self.user_agent
        if self.ip_address is not None:
            query_params['ip_address'] = self.ip_address
        t0 = time.perf_counter()
        if request_body is not None and not isinstance(request_body, dict):
            request_body = jsonpickle.encode(request_body)
        async with self.session.request(method, self.url + url, json=request_body, params=query_params) as response:
            res = await response.text()
            res = json.loads(res, object_hook=self._parse_value)
            if response.status != 200:
                raise Exception(res)

            logging.info(f"Time Request: {time.perf_counter() - t0:2.5f} {url:32} - {ResponseType.__name__}")
            return self._hangle_result(res, ResponseType)

    @abc.abstractmethod
    async def handle_exception(self, e: BaseException, url: str, method: str, ResponseType: Type[T], request_body=None, **query_params):
        pass


class HttpClientController(BaseClientController, metaclass=abc.ABCMeta):
    def get(self, url: str, response_type: Type[T], **query_params):
        return self.request(url, "get", response_type, **query_params)

    def post(self, url: str, request_body: object, response_type: Type[T], **query_params):
        return self.request(url, "post", response_type, request_body=request_body, **query_params)

    def put(self, url: str, request_body: object, response_type: Type[T], **query_params):
        return self.request(url, "put", response_type, request_body=request_body, **query_params)

    def delete(self, url: str, response_type: Type[T], **query_params):
        return self.request(url, "delete", response_type, **query_params)

    def _request(self, url: str, method: str, ResponseType: Type[T], *, request_body=None, **query_params):
        if self.user_agent is not None:
            query_params['user_agent'] = self.user_agent
        if self.ip_address is not None:
            query_params['ip_address'] = self.ip_address
        t0 = time.perf_counter()
        if request_body is not None:
            request_body = jsonpickle.encode(request_body)
        response = self.session.request(method, self.url + url, data=request_body, params=query_params)
        res = response.json(object_hook=self._parse_value)
        logging.info(f"Time Request: {time.perf_counter() - t0:2.5f} {url:32} - {ResponseType.__name__}")
        return self._hangle_result(res, ResponseType)

    def request(self, url: str, method: str, ResponseType: Type[T], *, request_body=None, **query_params):
        try:
            return self._request(url, method, ResponseType, request_body=request_body, **query_params)
        except BaseException as e:
            self.handle_exception(e, self.url + url, method, ResponseType, request_body, **query_params)

    @abc.abstractmethod
    def handle_exception(self, e: BaseException, url: str, method: str, ResponseType: Type, request_body,
                         **query_params):
        pass
