import platform
import uuid

from desktop_app.Controllers.QtHttpClientController import QtHttpClientController
from desktop_app.Models import Test


class TestController:

    def __init__(self):
        self.client = QtHttpClientController("".join(platform.uname()))

    def get_completed_test(self):
        return self.client.get('/completed_test', Test)

    def get_available_test(self):
        return self.client.get('/available_test', Test)

    def get_created_test(self):
        return self.client.get('/created_test', Test)

    def get_by_id(self, id_: uuid.UUID):
        return self.client.get('/test', Test, aId=str(id_))

    def create(self, test):
        test.theory = str(test.theory.id)
        return self.client.post('/test', test, Test)

    def get_count_attempts(self, test_id):
        return self.client.get("/available_count_attempts", int, test_id=test_id)
