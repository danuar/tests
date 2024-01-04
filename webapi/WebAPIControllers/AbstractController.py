from classy_fastapi import Routable
from fastapi import FastAPI


class AbstractController(Routable):

    @staticmethod
    def run(app: FastAPI):
        for Controller in AbstractController.__subclasses__():
            name = Controller.__name__
            app.include_router(Controller().router, tags=[name])
