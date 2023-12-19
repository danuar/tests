#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from asyncpg import UniqueViolationError
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from webapi.db import User
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.InterfacesControllers.StorageControllers.ICachedService import ICachedService
from webapi.InterfacesControllers.StorageControllers.IUserRepository import IUserRepository
from webapi.ViewModel import UserViewModel
from webapi.db.DbSession import DbSession


class UserRepository(IUserRepository, AbstractDbRepository):
    def __init__(self):
        super().__init__()
        self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]()
        self.session = DbSession().async_session

    async def RegisterOrAuthorize(self, aUser: UserViewModel) -> UserViewModel:
        aUser.CanBeCreated().raiseValidateException()
        user = User.CreateFrom(aUser)
        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            user = await self.Get(UserViewModel.Create(aUser.ipaddress, aUser.user_agent))
            if user is None:
                raise e
        user.SetToken(user.id)
        self.cachedService.Set(f"User.Token.{user.token}", user)
        return user

    async def Get(self, aUser: UserViewModel) -> UserViewModel:
        aUser.CanBeFind().raiseValidateException()
        user = None
        if aUser.id is not None:
            user = await self.session.get(User, aUser.id)
        elif aUser.ipaddress is not None and aUser.user_agent is not None:
            user = (await self.session.execute(select(User)
                                               .where((User.ipAddress == aUser.ip_address) |
                                                      (User.userAgent == aUser.user_agent)))).scalar()
        elif aUser.ipaddress is not None:
            user = (await self.session.execute(select(User).filter(User.ipAddress == aUser.ip_address))).scalar()
        elif aUser.user_agent is not None:
            user = (await self.session.execute(select(User).filter(User.userAgent == aUser.user_agent))).scalar()

        if user is not None:
            return user.GetViewModel()

    async def GetFromSessionToken(self, aToken: str) -> UserViewModel:
        await self._pass()
        return self.cachedService.TryGet(f"User.Token.{aToken}")

    async def _pass(self):
        pass
