import abc
import datetime
import logging
import time
import uuid
from typing import Type, Optional, TypeVar

import aiohttp
import jsonpickle
import requests
from dacite import from_dict, Config

from config import API_URL

T = TypeVar("T")


class AsyncHttpClientController:  # todo AsyncHttp привести к виду Http + вынести общую логику
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(cls)
        return cls.instance

    def __init__(self, user_agent: str = ""):
        if AsyncHttpClientController.instance is not None:
            return
        self.base_url = API_URL
        self.user_agent = user_agent
        self.session = aiohttp.ClientSession()
        AsyncHttpClientController.instance = self

    async def get(self, url: str, response_object: Type[T], **query_params):
        return await self.request(url, "get", response_object, **query_params)

    async def post(self, url: str, request_body: Type[T], response_object: object, **query_params):
        return await self.request(url, "post", response_object, request_body=request_body, **query_params)

    async def put(self, url: str, request_body: Type[T], response_object: object, **query_params):
        return await self.request(url, "put", response_object, request_body=request_body, **query_params)

    async def delete(self, url: str, response_object: Type[T], **query_params):
        return await self.request(url, "delete", response_object, **query_params)

    async def request(self, url: str, method: str, ResponseType: Type[T], *, request_body=None, **query_params):
        if self.user_agent is not None:
            query_params['user_agent'] = self.user_agent
        t0 = time.perf_counter()
        async with self.session.request(method, self.base_url + url, json=request_body,
                                        params=query_params) as response:
            res = await response.json()
            print(f"Time Request: {url} - {ResponseType.__name__}", time.perf_counter() - t0)
            if hasattr(res, 'detail'):
                raise Exception(res.detail)
            if isinstance(res, list):
                return [ResponseType(**i) for i in res]
            return res


class HttpClientController(metaclass=abc.ABCMeta):
    instance = None

    def __new__(cls, *args, **kwargs):
        if HttpClientController.instance is None:
            return super().__new__(cls)
        return HttpClientController.instance

    def __init__(self, user_agent: Optional[str] = None):
        if HttpClientController.instance is not None:
            return
        self.url = API_URL
        self.user_agent = user_agent
        self.session = requests.session()
        HttpClientController.instance = self

    def get(self, url: str, response_type: Type[T], **query_params):
        return self.request(url, "get", response_type, **query_params)

    def post(self, url: str, request_body: object, response_type: Type[T], **query_params):
        return self.request(url, "post", response_type, request_body=request_body, **query_params)

    def put(self, url: str, request_body: object, response_type: Type[T], **query_params):
        return self.request(url, "put", response_type, request_body=request_body, **query_params)

    def delete(self, url: str, response_type: Type[T], **query_params):
        return self.request(url, "delete", response_type, **query_params)

    def request(self, url: str, method: str, ResponseType: Type[T], *, request_body=None, **query_params):
        try:
            return self._request(url, method, ResponseType, request_body=request_body, **query_params)
        except BaseException as e:
            self.handle_exception(e, self.url + url, method, ResponseType, request_body, **query_params)

    @abc.abstractmethod
    def handle_exception(self, e: BaseException, url: str, method: str, ResponseType: Type, request_body,
                         **query_params):
        pass

    def _request(self, url: str, method: str, ResponseType: Type[T], *, request_body=None, **query_params):
        if self.user_agent is not None:
            query_params['user_agent'] = self.user_agent
        t0 = time.perf_counter()
        if request_body is not None:
            request_body = jsonpickle.encode(request_body)
        response = self.session.request(method, self.url + url, data=request_body, params=query_params)
        res = response.json(object_hook=self._parse_value)
        config = Config(check_types=False, )
        logging.info(f"Time Request: {time.perf_counter() - t0:2.5f} {url:32} - {ResponseType.__name__}")
        if ResponseType is dict:
            return res
        if isinstance(res, list):
            return [from_dict(ResponseType, i, config) for i in res]
        if isinstance(res, dict):
            return from_dict(ResponseType, res, config)
        return ResponseType(res) if res is not None else None

    def _parse_value(self, json: dict):
        for key, value in json.items():
            if isinstance(value, str):
                res = self._parse(value, datetime.datetime.fromisoformat)
                res = self._parse(res, datetime.time.fromisoformat)
                res = self._parse(res, uuid.UUID)
                json[key] = res
        # type_ = json.get("type", None)
        # if type_ is not None:
        #     json.pop("type")
        # if type_ == "QuestionChoice":
        #     return QuestionChoice(**json)
        # if type_ == "QuestionNotCheck":
        #     return QuestionNotCheck(**json)
        # if type_ == "QuestionInputAnswer":
        #     return QuestionInputAnswer(**json)
        return json

    @staticmethod
    def _parse(value: str, func):
        try:
            if value.isdigit(): return value
            value = func(value)
        except:
            pass
        return value
