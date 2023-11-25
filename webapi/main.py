import uvicorn
from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from webapi.WebAPIControllers import *

from webapi.ImplementationControllers import *  # define dependences
from webapi.WebAPIControllers.AbstractController import AbstractController

app = FastAPI()
AbstractController.run(app)


if __name__ == "__main__":
    uvicorn.run("webapi.main:app", host='127.0.0.1', port=9002, reload=True)
