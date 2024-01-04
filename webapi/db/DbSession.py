#!/usr/bin/python
# -*- coding: UTF-8 -*-

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import config


class DbSession(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(cls)
        return cls.instance

    def __init__(self):
        if DbSession.instance is not None:
            return
        engine_psql = create_async_engine(
            f'postgresql+asyncpg://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}'
            f'@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}',
            pool_pre_ping=True,
        )
        self.session = sessionmaker(engine_psql, class_=AsyncSession, expire_on_commit=False)
        self.async_session: AsyncSession = self.session()

        DbSession.instance = self
