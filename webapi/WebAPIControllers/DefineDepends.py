import ipaddress
import logging
from typing import Optional

from fastapi import Response, Request, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from webapi.InterfacesControllers import IUserLogic, ICachedService
from webapi.ViewModel import UserViewModel
from webapi.db import DbSession


def get_user_logic() -> IUserLogic:
    return IUserLogic.__subclasses__()[-1]()


def get_cached_service() -> ICachedService:
    return ICachedService.__subclasses__()[-1]()


async def get_async_session() -> AsyncSession:
    async with DbSession().session().begin() as session:
        try:
            DbSession().async_session = session
            yield session
        except Exception as e:
            session.rollback()
            raise e


async def get_user(request: Request,
                   response: Response,
                   user_agent: Optional[str] = None,
                   token: Optional[str] = Cookie(default=None)) -> Optional[UserViewModel]:
    logic = get_user_logic()
    user = await logic.GetFromSession(token)
    if user is None:
        int_ipaddress = int(ipaddress.ip_address(request.client.host))
        try:
            user = await logic.RegisterOrAuthorize(UserViewModel.Create(int_ipaddress, user_agent))
        except Exception:
            if user_agent is None:
                raise Exception("Не заполнен UserAgent")
        if user is None:
            logging.warning(f"Не удалось получить пользователя: {int_ipaddress=} {user_agent=}, {token=}")
        response.set_cookie("token", user.token)
    return user


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except BaseException as e:
        logging.info("Произошла ошибка", exc_info=e)
        return JSONResponse(content={"error": str(e.__class__.__name__), "detail": str(e)}, status_code=400)
