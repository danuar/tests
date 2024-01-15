import datetime
import uuid
from dataclasses import dataclass, field
from typing import Optional, Union
from uuid import UUID


@dataclass
class AnswerTest:
    text: str
    is_correct: bool
    id: UUID = None
    question: 'QuestionChoice' = None
    answers: list['Answer'] = field(default_factory=lambda: [])


@dataclass
class Answer:
    id: UUID = None
    mark: int = 0
    complition_time: Optional[datetime.datetime] = None
    text_answer: Optional[str] = None
    question: Union['QuestionChoice', 'QuestionInputAnswer', 'QuestionNotCheck'] = None
    result_test: 'ResultTest' = None
    answers_test: list[AnswerTest] = field(default_factory=lambda: [])


@dataclass
class ChapterTheory:
    name: str
    id: Optional[UUID] = None
    theory: 'Theory' = None
    pointers: list['PointerToAnswer'] = None
    content: Optional[str] = None


@dataclass
class PointerToAnswer:
    start: int
    end: int
    id: UUID = None
    question: 'Question' = None
    chapter: 'ChapterTheory' = None


@dataclass
class Question:
    name: str
    id: UUID = None
    complition_time: Optional[datetime.datetime] = None
    weight: int = 1
    pointer: PointerToAnswer = None
    test: 'Test' = None


@dataclass
class QuestionInputAnswer:
    name: str
    correct_answer: str
    k_misspell: float
    id: UUID = None
    complition_time: Optional[datetime.datetime] = None
    weight: int = 1
    pointer: PointerToAnswer = None
    test: 'Test' = None


@dataclass
class QuestionChoice:
    name: str
    answers_test: list[AnswerTest]
    id: UUID = None
    complition_time: Optional[datetime.datetime] = None
    weight: int = 1
    pointer: PointerToAnswer = None
    test: 'Test' = None


@dataclass
class QuestionNotCheck:
    name: str
    id: UUID = None
    complition_time: Optional[datetime.datetime] = None
    weight: int = 1
    pointer: PointerToAnswer = None
    test: 'Test' = None


@dataclass
class ResultTest:
    test: 'Test'
    answers: list[Answer] = field(default_factory=lambda: [])
    start_date: datetime.datetime = datetime.datetime.now()
    completed_date: Optional[datetime.datetime] = None
    note: Optional[str] = None
    id: UUID = None
    user: 'User' = None
    success: bool = False


@dataclass
class Theory:
    name: str
    study_time: Optional[datetime.time] = None
    tests: list['Test'] = None
    chapters: list[ChapterTheory] = None
    creator: Optional['User'] = None
    id: UUID = None


@dataclass
class User:
    id: uuid.UUID = None
    ipaddress: str = None
    userAgent: str = None


@dataclass
class Test:
    name: str
    theory: Theory
    id: UUID = None
    complition_time: Optional[datetime.datetime] = None
    count_attempts: int = None
    user: User = None
    shuffle: bool = False
    show_answer: bool = False
    questions: list[Union[QuestionChoice, QuestionInputAnswer, QuestionNotCheck]] = field(default_factory=lambda: [])


@dataclass
class ResultTestEasy:
    id: uuid.UUID
    completed_date: datetime.datetime
    mark: int
    all_mark: int
    complition_time: datetime.time
    note: str
    checked: bool
    name_test: str
