from dataclasses import dataclass
import datetime
import random

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import *

Base = declarative_base()


@dataclass
class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True,
                default="CAST(EXTRACT(EPOCH FROM NOW()) * 1000 AS INT)")
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now())
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
