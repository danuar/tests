from sqlalchemy.orm import backref

from db.Base import *


class PointerToAnswer(BaseModel):
    __tablename__ = 'pointers_to_answer'
    chapter_id = Column(Uuid(), ForeignKey('chapters_theory.id'))
    chapter = relationship('ChapterTheory', backref="pointers_to_answer", lazy=False)
    question_id = Column(Uuid(), ForeignKey('questions.id'))
    question = relationship("Question", backref=backref("pointer_to_answer", uselist=False, lazy=False), uselist=False)
    start = Column(Integer(), nullable=False)
    end = Column(Integer(), nullable=False)

    __table_args__ = (
        CheckConstraint('start >= 0', name='start_check'),
        CheckConstraint('"end" >= 0', name='end_check'),
    )
