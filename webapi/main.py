import uvicorn
from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

import config

# define dependences
from webapi.WebAPIControllers import *
from webapi.ImplementationControllers import *

from webapi.WebAPIControllers.DefineDepends import catch_exceptions_middleware
from webapi.WebAPIControllers.AbstractController import AbstractController

app = FastAPI()
app.middleware('http')(catch_exceptions_middleware)
AbstractController.run(app)


if __name__ == "__main__":
    uvicorn.run("webapi.main:app", host="127.0.0.1", port=int(config.API_PORT), reload=True)
