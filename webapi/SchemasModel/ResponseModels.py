import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from webapi.SchemasModel import *


class IdSchema(BaseModel):
    id: uuid.UUID


class UserResponseSchema(IdSchema):
    ip_address: str
    user_agent: str
    tests: list[str]
    results_tests: list[str]
    token: str


class TheoryResponseSchema(IdSchema):
    name: str
    study_time: Optional[datetime.time]
    creator: UserResponseSchema

    chapters: list[ChapterTheorySchema]
