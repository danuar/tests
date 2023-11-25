from pydantic import BaseModel

from webapi.ViewModel import UserViewModel


class UserSchema(BaseModel):
    ipaddress: str
    userAgent: str
