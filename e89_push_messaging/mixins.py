# -*- coding: utf-8 -*-
import copy

class PushMixin(object):

	def set_include_notify(self, registration_id_list):
		''' Recebe uma lista de registration id's adicionais que devem receber notificação push.'''
		self.include_notify = [i for i in list(registration_id_list) if i is not None]

	def set_exclude_notify(self,registration_id_list):
		''' Recebe uma lista de registration id's que não devem receber notificação push.'''
		self.exclude_notify = [i for i in list(registration_id_list) if i is not None]

	def set_ignore_alert(self, owner_ids=[]):
		if not owner_ids:
			self.ignore_alert = True
		else:
			self.ignore_alert = [i for i in list(owner_ids) if i is not None]

	def get_ignore_alert(self):
		if not hasattr(self, 'ignore_alert'):
			return False
		ignore = self.ignore_alert
		self.ignore_alert = False
		return ignore

	def get_include_notify(self):
		if not hasattr(self, 'include_notify'):
			return []

		include = copy.deepcopy(self.include_notify)
		self.include_notify = []
		return include

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

	def notify_owners(self):
		''' This method should never be used inside a transaction, or else if the push message arrives before the transaction is committed,
			the user will not receive the correct data.'''
		import e89_push_messaging.signals
		e89_push_messaging.signals.notify_owner(self._meta.model, self, None)
