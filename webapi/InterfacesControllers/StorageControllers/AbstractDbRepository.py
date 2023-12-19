#!/usr/bin/python
# -*- coding: UTF-8 -*-

from webapi.InterfacesControllers.StorageControllers.ICachedService import ICachedService
from webapi.db.DbSession import DbSession


class AbstractDbRepository(object):
	def __init__(self):
		self.session: DbSession = DbSession()
		self.cachedService: ICachedService = ICachedService.__subclasses__()[-1]
