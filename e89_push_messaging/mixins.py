# -*- coding: utf-8 -*-
import copy

class PushMixin(object):

	def set_exclude_notify(self,registration_id_list):
		''' Recebe uma lista de registration id's que não devem receber notificação push.'''
		self.exclude_notify = registration_id_list

	def get_exclude_notify(self):
		if not hasattr(self, 'exclude_notify'):
			return []

		exclude = copy.deepcopy(self.exclude_notify)
		self.exclude_notify = []
		return exclude

	def set_notify(self,notify):
		''' Booleano que indica se uma notificação push deve ou não ser enviada. Esse valor deve ser setado antes de salvar o objeto.'''
		self.notify = notify

	def get_notify(self):
		if not hasattr(self, 'notify'):
			return True
		return self.notify