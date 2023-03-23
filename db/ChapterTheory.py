from sqlalchemy import String, Column, VARCHAR, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db.Base import BaseModel


class ChapterTheory(BaseModel):
    __tablename__ = "chapters_theory"
    name = Column(VARCHAR(64))
    theory_id = Column(Integer(), ForeignKey('theories.id'))
    theory = relationship("Theory", backref='chapters')
