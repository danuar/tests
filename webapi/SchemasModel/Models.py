import datetime
import uuid
from typing import Optional, Union

from pydantic import BaseModel

from webapi.ViewModel import UserViewModel, TheoryViewModel, ChapterTheoryViewModel


class UserSchema(BaseModel):
    ipaddress: str
    userAgent: str


class TheorySchema(BaseModel, TheoryViewModel):
    name: str
    studyTime: Optional[datetime.time]


class ChapterTheorySchema(BaseModel, ChapterTheoryViewModel):
    name: str
    theory: Union[uuid.UUID, TheorySchema]


class ChapterTheoryUpdateSchema(BaseModel):
    name: str
