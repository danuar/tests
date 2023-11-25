import ipaddress
from typing import Union, Optional

from fastapi import Response, Request, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from webapi.InterfacesControllers import IUserLogic
from webapi.ViewModel import UserViewModel
from webapi.db import DbSession


def get_user_logic() -> IUserLogic:
    return IUserLogic.__subclasses__()[-1]()


async def get_async_session() -> AsyncSession:
    async with DbSession().session.begin() as session:
        DbSession().async_session = session
        yield session


async def get_user(request: Request,
                   response: Response,
                   user_agent: str,
                   token: Optional[str] = Cookie(default=None)) -> Optional[UserViewModel]:
    logic = get_user_logic()
    user = await logic.GetFromSession(token)
    if user is None:
        int_ipaddress = int(ipaddress.ip_address(request.client.host))
        result = await logic.RegisterOrAuthorize(UserViewModel.Create(int_ipaddress, user_agent))
        response.set_cookie("token", result.token)
        return result
