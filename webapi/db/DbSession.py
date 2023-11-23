#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import config


class DbSession(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        engine_psql = create_engine(
            f'postgresql://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}'
            f'@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}',
            pool_pre_ping=True,
        )
        self.session = Session(bind=engine_psql)
        self.session.expire_on_commit = False
