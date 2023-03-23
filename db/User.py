from sqlalchemy.orm import relationship

from db.Base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'
