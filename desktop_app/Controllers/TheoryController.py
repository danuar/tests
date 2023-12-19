import asyncio
import json
import os
import platform

import jsonpickle

from ClientController import HttpClientController, AsyncHttpClientController
from desktop_app.Controllers.QtHttpClientController import QtHttpClientController
from desktop_app.Models import Theory


class TheoryController:

    def __init__(self):
        self.client = QtHttpClientController("".join(platform.uname()))

    def get_created_theories(self):
        return self.client.get("/theories", Theory, get_content=True)

    def create_theory(self, theory: Theory):
        return self.client.post("/theory", theory, Theory)

    def update_theory(self, theory: Theory):
        return self.client.put("/theory", theory, Theory, aId=theory.id)
