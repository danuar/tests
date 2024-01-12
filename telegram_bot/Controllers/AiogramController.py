import asyncio
from typing import Type, Optional

from aiogram import Bot

from ClientController import AsyncHttpClientController


class AiogramController(AsyncHttpClientController):
    async def handle_exception(self, e: BaseException, url: str, method: str, ResponseType: Type, request_body=None,
                               **query_params):
        if self.chat_id is None or self.bot is None:
            raise Exception("Not filled attribute chat_id or bot")
        await self.bot.send_message(self.chat_id, f"""Возникла ошибка при запросе к серверу.
        Exception: *{e}*.
        URL: *{url}*.
        Method: *{method}*.
        Request body: *{request_body}*.
        Response Type: *{ResponseType}*.
        Query params: *{query_params}*.
        """, parse_mode='markdown')

    def set_bot(self, bot: Bot) -> 'AiogramController':
        self.bot = bot
        return self

    def set_chat_id(self, chat_id: int) -> 'AiogramController':
        self.chat_id = chat_id
        return self

    def set_ip_address(self, ip_address: str):
        self.ip_address = ip_address
        return self

    def __init__(self, user_agent: Optional[str] = None):
        super().__init__(user_agent)
        self.chat_id: Optional[int] = None
        self.bot: Optional[Bot] = None
        self.ip_address: Optional[str] = None
