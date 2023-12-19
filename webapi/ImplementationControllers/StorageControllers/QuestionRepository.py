#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import Type

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from webapi.InterfacesControllers import IQuestionRepository, ICachedService, IUserRepository
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.ViewModel import *
from webapi.db import DbSession, Question, PointerToAnswer


class QuestionRepository(IQuestionRepository, AbstractDbRepository):
    def __init__(self):
        super().__init__()
        self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]()
        self.user_repository: IUserRepository = IUserRepository.__subclasses__()[-1]()
        self.session = DbSession().async_session

    async def Create(self, user: UserViewModel, aQuestion: QuestionViewModel) -> QuestionViewModel:
        aQuestion.CanBeCreated().raiseValidateException()
        QuestionType = Question.get_type_in_db(aQuestion)
        question: Question = QuestionType.CreateFrom(aQuestion)
        self.session.add(question)
        await self.session.flush()
        resultQuestion = ((await self.session.execute(
            select(QuestionType).
            where(QuestionType.id == question.id).options(
                joinedload(QuestionType.question).
                joinedload(Question.test)))).
            unique().scalar_one())
        await self._validate_question(user.id, resultQuestion.question)
        await self.session.commit()
        return resultQuestion.GetViewModel()

    async def Update(self, user: UserViewModel, aQuestion: QuestionViewModel) -> QuestionViewModel:
        question = await self.session.get(Question, aQuestion.id)
        await self._validate_question(user.id, question)
        question.name = aQuestion.name
        question.complition_time = aQuestion.complition_time
        question.weight = aQuestion.weight
        question.pointer_to_answer = PointerToAnswer.CreateFrom(aQuestion.pointer)
        await self._validate_question(user.id, question)
        await self.session.commit()
        return question.GetViewModel()

    async def Delete(self, user: UserViewModel, aQuestion: QuestionViewModel) -> QuestionViewModel:
        aQuestion.CanBeDeleted().raiseValidateException()
        question = (await self.session.get(Question.get_type_in_db(aQuestion), aQuestion.id))
        await self._validate_question(user.id, question)
        await self.session.delete(question)
        await self.session.commit()
        return question.GetViewModel()

    async def Get(self, aQuestion: QuestionViewModel) -> QuestionViewModel:
        aQuestion.CanBeFind().raiseValidateException()
        return (await self.session.get(Question, aQuestion.id, options=[joinedload(Question.pointer_to_answer)
                                       .joinedload(PointerToAnswer.chapter)])).GetViewModel()

    async def DeletePointerFromQuestion(self, user: UserViewModel, aQuestion: QuestionViewModel) -> QuestionViewModel:
        aQuestion.CanBeFind().raiseValidateException()
        question: Question = await self.session.get(Question, aQuestion.id)
        await self._validate_question(user.id, question)
        question.pointer_to_answer = None
        await self.session.commit()
        return question.GetViewModel()

    async def GetFromTest(self, aTest: TestViewModel) -> List[QuestionViewModel]:
        result = (await self.session.execute(select(Question).where(Question.test_id == aTest.id).options(
            joinedload(Question.pointer_to_answer).
            joinedload(PointerToAnswer.chapter))))
        return [i.GetViewModel() for i in result.unique().scalars()]

    async def _validate_question(self, user_id, question: Question) -> Type[Question]:
        if question is None:
            raise Exception("Неверно задан id для вопроса")
        if question.test.creator_id != user_id:
            await self.session.rollback()
            raise Exception("Менять вопрос может только создатель теста с этим вопросом")
