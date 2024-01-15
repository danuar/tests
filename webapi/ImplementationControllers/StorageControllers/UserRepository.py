#!/usr/bin/python
# -*- coding: UTF-8 -*-

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.InterfacesControllers.StorageControllers.ICachedService import ICachedService
from webapi.InterfacesControllers.StorageControllers.IUserRepository import IUserRepository
from webapi.ViewModel import UserViewModel
from webapi.db import User
from webapi.db.DbSession import DbSession


class UserRepository(IUserRepository, AbstractDbRepository):
    async def RegisterOrAuthorize(self, aUser: UserViewModel) -> UserViewModel:
        aUser.CanBeCreated().raiseValidateException()
        user = await self.Get(aUser)
        if user is None:
            if aUser.user_agent is None:
                raise Exception("New user must have filled user_agent")
            user = User.CreateFrom(aUser)
            self.session.add(user)
            await self.session.commit()
            user = user.GetViewModel()
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
