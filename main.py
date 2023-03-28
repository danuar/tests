import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session

import config
from db import *
from db.Questions.QuestionChoise import QuestionChoise

engine = create_engine(
        f'postgresql+psycopg2://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}',
        pool_pre_ping=True,
        echo=True
    )

session_factory = sessionmaker(bind=engine)

db_session = Session(bind=engine)

print(QuestionChoise())
db_session.add(User())
db_session .commit()

