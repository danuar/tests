#!/usr/bin/python
# -*- coding: UTF-8 -*-
import abc

from webapi.InterfacesControllers.StorageControllers.ICachedService import ICachedService
from webapi.db.DbSession import DbSession


class AbstractDbRepository:
	def __init__(self, session: DbSession):
		self.db_session: DbSession = session
		self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]()

	@property
	def session(self):
		return self.db_session.async_session
