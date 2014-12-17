# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import timezone
from django.db.models import get_model,Q
import urllib2,json,time
import datetime as dt
import logging
import sys
from apns import APNs, Frame, Payload
import e89_push_messaging.push_tools

def send_message_ios(owners, data_dict={'type':'update'}, exclude_reg_ids=[]):

	# Looking for devices
    Device = get_model("e89_push_messaging", "Device")
    devices = Device.objects.filter(Q(owner__in=owners),Q(platform="ios"),~Q(registration_id__in=exclude_reg_ids))
    registration_ids = list(devices.values_list("registration_id",flat=True))

    e89_push_messaging.push_tools.print_console("Sending message APNS to reg_ids: " + ",".join([r for r in registration_ids]))

    # Sending request
    if len(registration_ids) == 0:
        return

    if settings.DEBUG:
    	apns = APNs(use_sandbox=True, cert_file=settings.APNS_DEV_CERTIFICATE, key_file=settings.APNS_DEV_KEY)
    else:
    	apns = APNs(use_sandbox=False, cert_file=settings.APNS_PROD_CERTIFICATE, key_file=settings.APNS_PROD_KEY)

    payload = Payload(custom=data_dict)
    frame = Frame()
    for idx,registration_id in enumerate(registration_ids):
    	frame.add_item(token_hex=registration_id, payload=payload, identifier=idx,
    		expiry=time.time() + 3600, priority=10)


    apns.gateway_server.send_notification_multiple(frame)