import datetime
from typing import Optional

from pydantic import BaseModel

from webapi.ViewModel import UserViewModel, TheoryViewModel


class UserSchema(BaseModel):
    ipaddress: str
    userAgent: str


class TheorySchema(BaseModel, TheoryViewModel):
    name: str
    studyTime: Optional[datetime.time]
