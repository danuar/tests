import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session

import config
from db.Base import Base
from db import *

engine = create_engine(
        f'postgresql://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}',
        pool_pre_ping=True,
        echo=True
    )

session_factory = sessionmaker(bind=engine)
db_session = Session(session_factory())

