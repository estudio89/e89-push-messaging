# -*- coding: utf-8 -*-
from django.apps import AppConfig

class E89PushMessagingConfig(AppConfig):
	name='e89_push_messaging'
	def ready(self):
		import e89_push_messaging.signals
