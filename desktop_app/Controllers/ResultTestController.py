import platform
import uuid
from typing import Optional

from desktop_app.Controllers.QtHttpClientController import QtHttpClientController
from desktop_app.Models import ResultTest, Answer, ResultTestEasy


class ResultTestController:

    def __init__(self):
        self.client = QtHttpClientController("".join(platform.uname()))

    def get_result_test_by_created_test(self):
        return self.client.get("/results_test_by_created_tests", ResultTest)

    def get_result_test_by_created_test_in_easy_format(self):
        return self.client.get("/results_test_by_created_tests_easy", ResultTestEasy)

    def get_result_test_by_user_in_easy_format(self):
        return self.client.get("/results_test_by_user_easy", ResultTestEasy)

    def get_result_test_by_user(self):
        return self.client.get("/my_results_test", ResultTest)

    def get_by_id(self, id_: uuid.UUID):
        return self.client.get("/result_test", ResultTest, aId=str(id_))

    def start_test(self, test_id: uuid.UUID, note: Optional[str] = None):
        return self.client.post("/result_test", {"test_id": str(test_id), "note": note}, ResultTest)

    def complete_test(self, result_test_id: uuid.UUID):
        return self.client.post("/complete_test", None, ResultTest, result_test_id=result_test_id)

    def update(self, result_test: ResultTest):
        return self.client.put("/result_test", result_test, ResultTest, aId=str(result_test.id))

    def add_answer(self, result_test_id: uuid.UUID, answer: Answer):
        answer.question_id = str(answer.question.id)
        return self.client.put("/add_answer", answer, Answer, result_test_id=str(result_test_id))

    def save_note(self, result_test_id: uuid.UUID, note: str):
        return self.client.put("/change_note", None, ResultTest, result_test_id=result_test_id, note=note)

    def set_marks_for_answers(self, answers: list[Answer]):
        return self.client.put("/mark_for_question_not_check", [
            {"answer_id": str(answer.id), "mark": answer.mark} for answer in answers
        ], ResultTest)
