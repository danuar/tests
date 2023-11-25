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
			user = await self.Get(UserViewModel.Create(None, aUser.userAgent))
			if user is None:
				user = await self.Get(UserViewModel.Create(aUser.ipAddress, None))
		user.SetToken(user.id)
		self.cachedService.Set(f"User.Token.{user.token}", user)
		return user

	async def Get(self, aUser: UserViewModel) -> UserViewModel:
		aUser.CanBeFind().raiseValidateException()
		# todo cache
		# result = self.cachedService.TryGet(f"User.Get.Id.{aUser.id}")
		#
		# if self.cachedService.result_last_operation:
		# 	return result
		# else:
		# 	result = await self.session.get(User, aUser.id)
		# 	self.cachedService.Set(f"User.Get.Id.{aUser.id}", result)
		# 	return result
		if aUser.id is not None:
			return await self.session.get(User, aUser.id)
		if aUser.ip_address is not None:
			return (await self.session.execute(select(User).filter(User.ipAddress == aUser.ip_address))).scalar()
		if aUser.userAgent is not None:
			return (await self.session.execute(select(User).filter(User.userAgent == aUser.userAgent))).scalar()

	async def GetFromSessionToken(self, aToken: str) -> UserViewModel:
		return self.cachedService.Get(f"User.Token.{aToken}")
