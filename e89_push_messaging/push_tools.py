# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import timezone
from django.db.models import get_model
import urllib2,json,time
import datetime as dt
import logging
import sys
import e89_push_messaging.android
import e89_push_messaging.ios

def send_message(owners, exclude_reg_ids=[], include_reg_ids=[],data_dict = {'type':'update'}, collapse_key="update"):
    e89_push_messaging.android.send_message_android(owners, exclude_reg_ids = exclude_reg_ids,include_reg_ids = include_reg_ids, data_dict = data_dict, collapse_key="update")
    e89_push_messaging.ios.send_message_ios(owners, exclude_reg_ids = exclude_reg_ids, include_reg_ids = include_reg_ids, data_dict = data_dict)

    print_console("Enviando mensagem push para: " + ", ".join([str(o) for o in owners]))

def register_device(owner,registration_id, platform):
    Device = get_model("e89_push_messaging", "Device")
    try:
    	device = Device.objects.get(registration_id=registration_id,platform=platform)
    except Device.DoesNotExist:
    	device = Device(registration_id=registration_id,platform=platform)
    device.owner = owner
    device.save()

def deepgetattr(obj, attr):
    """Recurses through an attribute chain to get the ultimate value."""
    value = reduce(getattr, attr.split('__'), obj)
    if hasattr(value, '__call__'):
        return value()
    return value

def print_console(msg):
    try:
        sys.stderr.write(msg + '\n')
    except UnicodeError:
        pass