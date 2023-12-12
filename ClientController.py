import datetime
import json
from types import SimpleNamespace

import jsonpickle
from typing import Type

import aiohttp
import requests


class AsyncHttpClientController:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(cls)
        return cls.instance

    def __init__(self, user_agent: str = ""):
        if AsyncHttpClientController.instance is not None:
            return
        self.base_url = "http://127.0.0.1:9002"
        self.user_agent = user_agent
        self.session = aiohttp.ClientSession()

    async def get(self, url: str, response_object: object, **query_params):
        return await self.request(url, "get", response_object, **query_params)

    async def post(self, url: str, request_body: object, response_object: object, **query_params):
        return await self.request(url, "post", response_object, request_body=request_body, **query_params)

    async def put(self, url: str, request_body: object, response_object: object, **query_params):
        return await self.request(url, "put", response_object, request_body=request_body, **query_params)

    async def delete(self, url: str, response_object: object, **query_params):
        return await self.request(url, "delete", response_object, **query_params)

    async def request(self, url: str, method: str, response_object: object, *, request_body=None, **query_params):
        async with self.session.request(method, self.base_url + url, json=request_body, params=query_params) as response:
            response_text = await response.text()
            res = json.loads(response_text, object_hook=lambda d: SimpleNamespace(**d))
            if hasattr(res, 'detail'):
                raise Exception(res.detail)
            return res


class HttpClientController:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(cls)
        return cls.instance

    def __init__(self, user_agent: str = ""):
        if HttpClientController.instance is not None:
            return
        self.url = "http://127.0.0.1:9002"
        self.user_agent = user_agent
        self.session = requests.session()

    def get(self, response_object: object, **query_params):
        self.request("delete", response_object, **query_params)

    def post(self, request_body: object, response_object: object, **query_params):
        self.request("put", response_object, request_body=request_body, **query_params)

    def put(self, request_body: object, response_object: object, **query_params):
        self.request("put", response_object, request_body=request_body, **query_params)

    def delete(self, response_object: object, **query_params):
        self.request("delete", response_object, **query_params)

    def request(self, method: str, response_object: object, *, request_body=None, **query_params):
        response = self.session.request(method, self.url, data=request_body, params=query_params)
        response_json = response.json()
        response_object.__dict__.update(response_json)
