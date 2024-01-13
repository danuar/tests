import platform
import uuid

from telegram_bot.Controllers.AiogramController import AiogramController
from telegram_bot.Models import Test, ResultTest, Answer
from ClientController import AsyncHttpClientController
from typing import Optional


class ResultTestController:

    def __init__(self):
        self.client = AiogramController()

    async def get_by_id(self, id_: uuid.UUID):
        return await self.client.get("/result_test", ResultTest, aId=str(id_))

    async def start_test(self, test_id: uuid.UUID, note: Optional[str] = None):
        return await self.client.post("/result_test", {"test_id": str(test_id), "note": note}, ResultTest)

    async def complete_test(self, result_test_id: uuid.UUID):
        return await self.client.post("/complete_test", None, ResultTest, result_test_id=str(result_test_id))

    async def update(self, result_test: ResultTest):
        return await self.client.put("/result_test", result_test, ResultTest, aId=str(result_test.id))

    async def add_answer(self, result_test_id: uuid.UUID, answer: Answer):
        answer.question_id = str(answer.question.id)
        answer.complition_time = answer.complition_time.isoformat()
        answer = {"question_id": answer.question_id, "text_answer": answer.text_answer, "answers_test": answer.answers_test, "complition_time": answer.complition_time}
        return await self.client.put("/add_answer", answer, Answer, result_test_id=str(result_test_id))

    async def save_note(self, result_test_id: uuid.UUID, note: str):
        return await self.client.put("/change_note", None, ResultTest, result_test_id=str(result_test_id), note=note)
