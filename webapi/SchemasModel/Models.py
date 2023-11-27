import datetime
import uuid
from typing import Optional, Union

from pydantic import BaseModel, Field

from webapi.ViewModel import UserViewModel, TheoryViewModel, ChapterTheoryViewModel


class UserSchema(BaseModel):
    ipaddress: str
    userAgent: str


class TheorySchema(BaseModel, TheoryViewModel):
    name: str
    studyTime: Optional[datetime.time]

    class WTChapterTheorySchema(BaseModel):
        name: str

    chapters: Optional[list[WTChapterTheorySchema]] = Field(default_factory=lambda: [])


class ChapterTheorySchema(BaseModel, ChapterTheoryViewModel):
    name: str
    theory: Union[TheorySchema, uuid.UUID]


class ChapterTheoryUpdateSchema(BaseModel):
    name: str


class TestSchema(BaseModel):
    name: str
    theory: Union[uuid.UUID, TheorySchema]
    count_attempts: Union[None, int] = Field(
        default=None, gt=0,
        title="Количество попыток прохождения для одного человека. По умолчанию неограниченное количество")
    complition_time: Optional[datetime.time] = Field(None,
                                                     title="Время прохождения теста. Если не указано для теста, "
                                                           "должно быть указано для каждого вопроса в тесте")
    shuffle: bool = Field(default=False, title="Перемешивать ли вопросы при каждом прохождении теста")
    show_answer: bool = Field(default=False, title="Показывать ли ответы на вопросы после прохождения")


class TestUpdateSchema(BaseModel):
    name: str
