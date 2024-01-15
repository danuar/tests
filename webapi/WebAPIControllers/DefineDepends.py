import ipaddress
import logging
from typing import Optional

from fastapi import Response, Request, Cookie, Depends
from pydantic import IPvAnyAddress
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
from starlette.responses import JSONResponse

from webapi.InterfacesControllers import *
from webapi.ViewModel import UserViewModel
from webapi.db import DbSession

async_session = DbSession.get_session_maker().begin()


def get_cached_service() -> ICachedService:
    return ICachedService.__subclasses__()[-1]()


async def get_async_session() -> AsyncSession:
    async with DbSession.get_session_maker()() as session:
        # session = transaction.session
        try:
            print('1'*100)
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        await session.commit()


async def get_db_session(session: AsyncSession = Depends(get_async_session)) -> DbSession:
    yield DbSession(session)


async def get_user_logic(session=Depends(get_db_session)) -> IUserLogic:
    repository = IUserRepository.__subclasses__()[-1](session)
    yield IUserLogic.__subclasses__()[-1](repository)


def get_chapter_logic(session=Depends(get_db_session)) -> IChapterLogic:
    repository = IChapterRepository.__subclasses__()[-1](session)
    yield IChapterLogic.__subclasses__()[-1](repository)


def get_theory_logic(session=Depends(get_db_session), chapter_logic=Depends(get_chapter_logic)) -> ITheoryLogic:
    repository = ITheoryRepository.__subclasses__()[-1](session)
    yield ITheoryLogic.__subclasses__()[-1](repository, chapter_logic)


def get_test_logic(session=Depends(get_db_session)) -> ITestLogic:
    repository = ITestRepository.__subclasses__()[-1](session)
    yield ITestLogic.__subclasses__()[-1](repository)


def get_question_logic(session=Depends(get_db_session)) -> IQuestionLogic:
    repository = IQuestionRepository.__subclasses__()[-1](session)
    yield IQuestionLogic.__subclasses__()[-1](repository)


def get_result_test_logic(session=Depends(get_db_session)) -> IResultTestLogic:
    repository = IResultTestRepository.__subclasses__()[-1](session)
    yield IResultTestLogic.__subclasses__()[-1](repository)


def get_passing_test_logic(session=Depends(get_db_session)) -> IPassingTestLogic:
    repository = IResultTestRepository.__subclasses__()[-1](session)
    yield IPassingTestLogic.__subclasses__()[-1](repository)


async def get_user(request: Request,
                   response: Response,
                   user_agent: Optional[str] = None,
                   ip_address: Optional[IPvAnyAddress] = None,
                   token: Optional[str] = Cookie(default=None),
                   logic=Depends(get_user_logic)) -> Optional[UserViewModel]:
    user = await logic.GetFromSession(token)
    if user:
        yield user
        return
    if ip_address:
        int_ipaddress = int(ipaddress.ip_address(ip_address))
    else:
        int_ipaddress = int(ipaddress.ip_address(request.client.host))
    user = await logic.RegisterOrAuthorize(UserViewModel.Create(int_ipaddress, user_agent))
    if user is None and user_agent is None:
        raise Exception("Не заполнен UserAgent")
    if user is None:
        logging.warning(f"Не удалось получить пользователя: {int_ipaddress=} {user_agent=}, {token=}")
        raise Exception("Не удалось получить пользователя")
    response.set_cookie("token", user.token)
    yield user


async def catch_exceptions_middleware(request: Request, call_next):

    try:
        return await call_next(request)
    except BaseException as e:
        logging.info("Произошла ошибка", exc_info=e)
        return JSONResponse(content={"error": str(e.__class__.__name__), "detail": str(e)}, status_code=400)
