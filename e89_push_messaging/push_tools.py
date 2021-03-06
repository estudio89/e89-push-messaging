# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import timezone
from django.apps import apps
from django.db import IntegrityError
import urllib2,json,time
import datetime as dt
import logging
import sys
import e89_push_messaging.android
import e89_push_messaging.ios
import e89_push_messaging.websockets

LOGGER = logging.getLogger(__name__)

def send_message(owners, exclude_reg_ids=[], include_reg_ids=[], data_dict = {'type':'update'}, payload_alert=None, collapse_key="update"):
    e89_push_messaging.android.send_message_android(owners, exclude_reg_ids = exclude_reg_ids,include_reg_ids = include_reg_ids, data_dict = data_dict, collapse_key=collapse_key)
    e89_push_messaging.ios.send_message_ios(owners, exclude_reg_ids = exclude_reg_ids, include_reg_ids = include_reg_ids, data_dict = data_dict, payload_alert = payload_alert)
    e89_push_messaging.websockets.send_message_websockets(owners, data_dict = data_dict)
    print_console("Enviando mensagem push para: " + ", ".join([str(o) for o in owners]))

def register_device(owner, registration_id, old_registration_id, platform, app_version):
    Device = apps.get_model("e89_push_messaging", "Device")
    if not old_registration_id:
        old_registration_id = registration_id

    try:
        device = Device.objects.update_or_create(registration_id=old_registration_id, platform=platform, defaults={"owner":owner, "registration_id":registration_id, "version":app_version})
    except IntegrityError as e:
        if not Device.objects.filter(registration_id=registration_id, platform=platform, owner=owner).exists():
            raise
        else:
            device = Device.objects.filter(registration_id=registration_id, platform=platform, owner=owner).first()
            device.version = app_version
            device.save()

def deepgetattr(obj, attr):
    """Recurses through an attribute chain to get the ultimate value."""
    value = reduce(getattr, attr.split('__'), obj)
    if hasattr(value, '__call__'):
        return value()
    return value

def print_console(msg):
    if not getattr(settings, "PUSH_DEBUG", False):
        return

    try:
        LOGGER.info(msg)
    except UnicodeError:
        pass

def is_id(value):
    return isinstance(value, (int, long))