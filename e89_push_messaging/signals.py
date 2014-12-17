# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.db.models.signals import pre_delete,post_save
from django.dispatch.dispatcher import receiver
from django.db.models import get_model
from django.conf import settings
import e89_push_messaging.push_tools
import sys

def notify_owner(sender,instance,**kwargs):

	# Verificando se é necessário o envio de push
	notify = getattr(instance, "notify", True)
	if not notify:
		if hasattr(instance, "notify"):
			instance.notify = True
		e89_push_messaging.push_tools.print_console('PUSH nao enviado.')
		return

	# Buscando parâmetro do sender que representa o owner
	app = sender._meta.app_label
	model = sender.__name__
	owner_attr = settings.PUSH_MODELS[app+"."+model]

	# Buscando owner
	owners = []
	if owner_attr:
		owner = e89_push_messaging.push_tools.deepgetattr(instance,owner_attr)
		owners = [owner]
	else:
		# Owner não especificado. Envia push para todos as instâncias da classe PUSH_DEVICE_OWNER_MODEL
		owner_app,owner_model = settings.PUSH_DEVICE_OWNER_MODEL.split('.')
		owner_model = get_model(owner_app,owner_model)
		owners = owner_model.objects.filter(device__isnull=False)

	try:
		exclude_reg_ids = instance.get_exclude_notify()
	except AttributeError:
		exclude_reg_ids = []
	e89_push_messaging.push_tools.print_console('Enviando push. Exclude = ' + str(exclude_reg_ids))
	e89_push_messaging.push_tools.send_message(owners,exclude_reg_ids)

for app_model in settings.PUSH_MODELS.keys():
	app,str_model = app_model.split('.')
	model = get_model(app,str_model)
	assert model is not None, "Model %s nao encontrado. Confira a sintaxe na opcao PUSH_MODELS."%app_model

	for signal in [pre_delete,post_save]:
		signal.connect(receiver=notify_owner,sender=model)
