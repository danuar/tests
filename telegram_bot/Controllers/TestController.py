import platform
import uuid

from telegram_bot.Controllers.AiogramController import AiogramController
from telegram_bot.Models import Test


class TestController:

    def __init__(self):
        self.client = AiogramController("".join(platform.uname()))

    async def get_pdf_test(self, test: Test) -> bytes:
        async with self.client.session.get(self.client.url + "/pdf", params={"aId": str(test.theory.id)}) as response:
            return await response.read()

    async def get_completed_test(self):
        return await self.client.get('/completed_test', Test)

    async def get_by_id(self, id_: uuid.UUID) -> Test:
        return await self.client.get('/test', Test, aId=str(id_))

    async def get_count_attempts(self, test_id):
        return await self.client.get("/available_count_attempts", int, test_id=str(test_id))
