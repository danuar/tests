import uuid
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now())
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
