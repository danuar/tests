#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

from webapi.db import User
from webapi.InterfacesControllers.StorageControllers.AbstractDbRepository import AbstractDbRepository
from webapi.InterfacesControllers.StorageControllers.ICachedService import ICachedService
from webapi.InterfacesControllers.StorageControllers.IUserRepository import IUserRepository
from webapi.ViewModel import UserViewModel
from webapi.db.DbSession import DbSession


class UserRepository(IUserRepository, AbstractDbRepository):
	def __init__(self):
		self.session = DbSession().session
		self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]

	async def RegisterOrAuthorize(self, aUser: UserViewModel) -> UserViewModel:
		aUser.CanBeCreated().raiseValidateException()
		try:
			await self.session.add(User.CreateFrom(aUser))
			return aUser
		except Exception as e:
			print(e)

	async def Get(self, aUser: UserViewModel) -> UserViewModel:
		aUser.CanBeFind().raiseValidateException()
		result = self.cachedService.TryGet(f"User.Get.Id.{aUser.id}")

		if self.cachedService.result_last_operation:
			return result
		else:
			result = await self.session.get(User, aUser.id)
			self.cachedService.Set(f"User.Get.Id.{aUser.id}", result)
			return result

	def GetFromSessionToken(self, aToken: str) -> UserViewModel:
		return self.cachedService.Get(f"User.Token.{aToken}")
