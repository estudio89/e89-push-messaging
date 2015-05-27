# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.db.models.signals import pre_delete,post_save
from django.dispatch.dispatcher import receiver
from django.apps import apps
from django.db.models.query import QuerySet
from django.conf import settings
import e89_push_messaging.push_tools
import sys


def should_send_push(instance):
	# Verificando se é necessário o envio de push
	notify = getattr(instance, "notify", True)
	if not notify:
		if hasattr(instance, "notify"):
			instance.notify = True
		e89_push_messaging.push_tools.print_console('PUSH nao enviado.')
		return False
	return True

def get_owners(instance, owner_attr):
	# Buscando owner
	owners = []
	if owner_attr:
		owner = e89_push_messaging.push_tools.deepgetattr(instance,owner_attr)
		if type(owner) != type([]) and not isinstance(owner, QuerySet):
			owners = [owner]
		else:
			owners = owner
	else:
		# Owner não especificado. Envia push para todos as instâncias da classe PUSH_DEVICE_OWNER_MODEL
		owner_app,owner_model = settings.PUSH_DEVICE_OWNER_MODEL.split('.')
		owner_model = apps.get_model(owner_app,owner_model)
		owners = owner_model.objects.filter(device__isnull=False)

	return owners

def notify_owner(sender,instance,**kwargs):
	if not should_send_push(instance):
		return

	# Buscando parâmetro do sender que representa o owner
	app = sender._meta.app_label
	model = sender.__name__
	app_model = app+"."+model
	owner_attr = settings.PUSH_MODELS[app_model]["owner_attr"]
	payload_alert = settings.PUSH_MODELS[app_model].get("payload_alert", None)

	# Buscando owner
	owners = get_owners(instance, owner_attr)

	try:
		exclude_reg_ids = instance.get_exclude_notify()
		include_reg_ids = instance.get_include_notify()
	except AttributeError:
		exclude_reg_ids = []
		include_reg_ids = []
	e89_push_messaging.push_tools.print_console('Enviando push. Exclude = ' + str(exclude_reg_ids))
	e89_push_messaging.push_tools.send_message(owners, exclude_reg_ids,include_reg_ids, payload_alert=payload_alert)



for app_model in settings.PUSH_MODELS.keys():
	model = apps.get_model(app_model)
	assert model is not None, "Model %s nao encontrado. Confira a sintaxe na opcao PUSH_MODELS."%app_model

	for signal in [pre_delete,post_save]:
		signal.connect(receiver=notify_owner,sender=model)
