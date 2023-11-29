import abc
import datetime
import uuid
from typing import Optional, Union, Type

from pydantic import BaseModel, Field, root_validator

from webapi.ViewModel import UserViewModel, TheoryViewModel, ChapterTheoryViewModel, QuestionChoiceViewModel, \
    QuestionViewModel, AnswerTestViewModel, QuestionInputAnswerViewModel, TestViewModel, PointerToAnswerViewModel, \
    QuestionNotCheckViewModel


class UserSchema(BaseModel):
    ipaddress: str
    userAgent: str


class TheorySchema(BaseModel, TheoryViewModel):
    name: str
    studyTime: Optional[datetime.time]

    class WTChapterTheorySchema(BaseModel):
        name: str

    chapters: Optional[list[WTChapterTheorySchema]] = Field(default_factory=lambda: [])

    def GetViewModel(self):
        return TheoryViewModel.Create(self.name, None, aStudyTime=self.studyTime,
                                      chapters=[ChapterTheoryViewModel.Create(i.name, None) for i in self.chapters])


class ChapterTheorySchema(BaseModel, ChapterTheoryViewModel):
    name: str
    theory: Union[TheorySchema, uuid.UUID]


class ChapterTheoryUpdateSchema(BaseModel):
    name: str


class PointerToAnswerSchema(BaseModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    chapter: Union[uuid.UUID, ChapterTheorySchema]

    @classmethod
    @root_validator
    def name_must_contain_space(cls, values):
        start = values.get('start')
        end = values.get('end')
        if end <= start:
            raise ValueError("Конец указателя должен быть больше его начала")
        return values

    def GetViewModel(self):
        chapter = ChapterTheoryViewModel.Get(self.chapter)
        if isinstance(self.chapter, ChapterTheoryViewModel):
            chapter = ChapterTheoryViewModel.Create(self.chapter.name, self.chapter.theory)
        return PointerToAnswerViewModel.Create(self.start, self.end).SetChapter(chapter)


class AnswerTestSchema(BaseModel):
    text: str
    isCorrect: bool = Field(False)


class BaseQuestionSchema(BaseModel, metaclass=abc.ABCMeta):
    name: str
    complition_time: Optional[datetime.time] = Field(title="Должно быть указано если нет времени прохождения теста")
    weight: Optional[int] = Field(gt=0)
    test: Union[None, uuid.UUID]
    pointer_to_answer: PointerToAnswerSchema

    def CreateQuestion(self, Question: Type[QuestionViewModel]):
        test = self.test.GetViewModel() if isinstance(self.test, TestSchema) else TestViewModel.GetFromId(self.test)
        return (Question.Create(self.name, self.weight, self.complition_time, test)
                .SetPointerToAnswer(self.pointer_to_answer.GetViewModel()))

    @abc.abstractmethod
    def GetViewModel(self):
        pass


class QuestionUpdateSchema(BaseModel):
    name: str
    complition_time: Optional[datetime.time] = Field(title="Должно быть указано если нет времени прохождения теста")
    weight: Optional[int] = Field(gt=0)
    pointer_to_answer: PointerToAnswerSchema


class QuestionChoiceSchema(BaseQuestionSchema):
    answer_choices_for_test: list[AnswerTestSchema]

    def GetViewModel(self):
        return self.CreateQuestion(QuestionChoiceViewModel).AddAnswers(
            [AnswerTestViewModel.CreateInQuestion(i.text, i.isCorrect) for i in self.answer_choices_for_test])


class QuestionInputAnswerSchema(BaseQuestionSchema):
    correct_answer: str
    k_misspell: float = Field(gt=0, le=1)

    def GetViewModel(self):
        return (self.CreateQuestion(QuestionInputAnswerViewModel)
                .SetKMisspell(self.k_misspell)
                .SetCorrectAnswer(self.correct_answer))


class QuestionNotCheckSchema(BaseQuestionSchema):
    def GetViewModel(self):
        return self.CreateQuestion(QuestionNotCheckViewModel)


class TestSchema(BaseModel):
    name: str
    theory: Union[uuid.UUID, TheorySchema]
    questions: list[Union[QuestionChoiceSchema, QuestionNotCheckSchema, QuestionInputAnswerSchema]]
    count_attempts: Union[None, int] = Field(
        default=None, gt=0,
        title="Количество попыток прохождения для одного человека. По умолчанию неограниченное количество")
    complition_time: Optional[datetime.time] = Field(None,
                                                     title="Время прохождения теста. Если не указано для теста, "
                                                           "должно быть указано для каждого вопроса в тесте")
    shuffle: bool = Field(default=False, title="Перемешивать ли вопросы при каждом прохождении теста")
    show_answer: bool = Field(default=False, title="Показывать ли ответы на вопросы после прохождения")

    def GetViewModel(self):
        return TestViewModel.Create(self.name, self.count_attempts, self.shuffle, self.show_answer, None,
                                    self.theory.GetViewModel() if isinstance(self.theory, TheorySchema)
                                    else TheoryViewModel.GetFromId(self.theory.id),
                                    self.complition_time).AddQuestions([i.GetViewModel() for i in self.questions])


class TestUpdateSchema(BaseModel):
    name: str
    questions: list[Union[QuestionChoiceSchema, QuestionNotCheckSchema, QuestionInputAnswerSchema]]
