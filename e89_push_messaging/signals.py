# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.apps import apps
from django.core.signals import request_finished
from django.db import transaction
from django.db.models.query import QuerySet
from django.db.models.signals import pre_delete,post_save
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.template import Template,Context
from e89_push_messaging.push_sender import PushSender
import e89_push_messaging.push_tools
import sys
import threading
import copy

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

def notify_owner(sender, instance, signal, queue=True, testing=False, **kwargs):
	if not should_send_push(instance):
		return

	app = sender._meta.app_label
	model = sender.__name__
	app_model = app+"."+model
	owner_attr = settings.PUSH_MODELS[app_model]["owner_attr"]

	if queue and not testing:
		# Code is being run inside a transaction. Add to queue
		add_to_queue(sender, instance, signal, owners=kwargs.get("owners", get_owners(instance, owner_attr)))
		return

	# Finding owner
	owners = kwargs.get("owners", get_owners(instance, owner_attr))

	# Checking if payload alert should be sent
	payload_alert = settings.PUSH_MODELS[app_model].get("payload_alert", None)
	owners_ignore_payload = [] # list of owners that should not receive payload alert
	ignore_alert = instance.get_ignore_alert()
	if signal == pre_delete:
		payload_alert = None
	elif ignore_alert:
		if type(ignore_alert) == type([]): # list of owners that should not receive payload alert
			owners_ignore_payload = ignore_alert
		else:
			# payload should not be sent to anyone
			payload_alert = None


	# Processing payload alert
	if payload_alert is not None:
		payload_alert = Template(payload_alert).render(Context({"instance": instance}, autoescape=False))

	# Getting push identifier
	identifier = settings.PUSH_MODELS[app_model].get("identifier", None)

	try:
		exclude_reg_ids = instance.get_exclude_notify()
		include_reg_ids = instance.get_include_notify()
	except AttributeError:
		exclude_reg_ids = []
		include_reg_ids = []

	e89_push_messaging.push_tools.print_console('Enviando push. Exclude = ' + str(exclude_reg_ids))

	if not testing:
		PushSender().send(owners = owners,
			exclude_reg_ids = exclude_reg_ids,
			include_reg_ids = include_reg_ids,
			owners_ignore_payload = owners_ignore_payload,
			payload_alert=payload_alert,
			data_dict={'type':'update','identifier':identifier},
			collapse_key="update" if identifier is None else "update_" + identifier)
	else:
		return owners, exclude_reg_ids, include_reg_ids, owners_ignore_payload, payload_alert

data = threading.local()
data.e89_push_queue = None
data.connection_data = None

def add_to_queue(sender, instance, signal=None, owners=[], **kwargs):
	if not hasattr(data, "e89_push_queue") or data.e89_push_queue is None:
		data.e89_push_queue = set([])

	data.e89_push_queue.add((sender, instance, signal, tuple(owners)))

	from django.db import connection
	if hasattr(connection, "threadlocal"):
		data.connection_data = copy.deepcopy(connection.threadlocal.__dict__)

	return

def process_queue(sender, **kwargs):
	if not hasattr(data, "e89_push_queue") or data.e89_push_queue is None:
		return

	from django.db import connection
	if hasattr(data, "connection_data") and data.connection_data is not None and hasattr(connection, "threadlocal"):
		for attr,value in data.connection_data.iteritems():
			setattr(connection.threadlocal, attr, value)

	for sender,instance,signal,owners in data.e89_push_queue:
		notify_owner(sender, instance, signal, queue=False, owners=owners)

	data.e89_push_queue = None
	data.connection_data = None

def connect_signals():
	# Connecting signals to model events
	for app_model in settings.PUSH_MODELS.keys():
		model = apps.get_model(app_model)
		send_on_save = settings.PUSH_MODELS[app_model].get("send_on_save", True)

		signals_list = [pre_delete]
		if send_on_save:
			signals_list.append(post_save)

		assert model is not None, "Model %s nao encontrado. Confira a sintaxe na opcao PUSH_MODELS."%app_model

		for signal in signals_list:
			signal.connect(receiver=notify_owner,sender=model)

	# Connecting signal to response sent event
	request_finished.connect(process_queue)

connect_signals()
