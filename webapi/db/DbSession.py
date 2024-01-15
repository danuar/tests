#!/usr/bin/python
# -*- coding: UTF-8 -*-

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import config


class DbSession:
    _engine_psql = create_async_engine(
        f'postgresql+asyncpg://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}'
        f'@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}',
        pool_pre_ping=True,
    )
    _session = sessionmaker(_engine_psql, class_=AsyncSession, expire_on_commit=False)

    @classmethod
    def get_session_maker(cls) -> sessionmaker:
        return cls._session

    def __init__(self, async_session: AsyncSession):
        self.async_session: AsyncSession = async_session
