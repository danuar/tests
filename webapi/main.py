import uvicorn
from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from webapi.WebAPIControllers import *

from webapi.ImplementationControllers import *  # define dependences
from webapi.WebAPIControllers.AbstractController import AbstractController
from webapi.db import DbSession

app = FastAPI()
AbstractController.run(app)


@app.middleware("http")
async def begin_async_session(request: Request, call_next):
    async with DbSession().session().begin() as session:
        DbSession().async_session = session
        return await call_next(request)


if __name__ == "__main__":
    uvicorn.run("webapi.main:app", host='127.0.0.1', port=9000, reload=True)
