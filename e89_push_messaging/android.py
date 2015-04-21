# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.apps import apps
import urllib2,json,time
import datetime as dt
import logging
import sys
import e89_push_messaging.push_tools

def send_message_android(owners, exclude_reg_ids=[], include_reg_ids=[], data_dict = {}, collapse_key="update"):

    # Looking for devices
    Device = apps.get_model("e89_push_messaging", "Device")

    # Verifying if owner id's were passed instead of reg id's
    if exclude_reg_ids and type(exclude_reg_ids[0]) == type(1):
        exclude_reg_ids = Device.objects.filter(owner_id__in=exclude_reg_ids).values_list('registration_id',flat=True)

    if include_reg_ids and type(include_reg_ids[0]) == type(1):
        include_reg_ids = Device.objects.filter(owner_id__in=include_reg_ids).values_list('registration_id',flat=True)

    devices = Device.objects.filter(Q(owner__in=owners) | Q(registration_id__in=include_reg_ids),Q(platform="android"),~Q(registration_id__in=exclude_reg_ids))

    registration_ids = list(devices.values_list("registration_id",flat=True))

    e89_push_messaging.push_tools.print_console("Sending message GCM to reg_ids: " + ",".join([r for r in registration_ids]))

    # Sending request
    if len(registration_ids) == 0:
        return
    results = _do_post(registration_ids, data_dict=data_dict,collapse_key=collapse_key)

    # Updating registration id's if needed
    for device,result in zip(devices,results):
        if result.get("registration_id") and result["registration_id"] != device.registration_id:
            device.registration_id = result["registration_id"]
            device.save()

def _do_post(registration_ids, data_dict={},collapse_key='update',wait=1):
    # Setting up request
    values = {'registration_ids':registration_ids,
              'collapse_key':collapse_key}
    if data_dict:
        values["data"] = data_dict

    headers = {'Authorization':'key=%s'%settings.GCM_API_KEY,
                'Content-Type':'application/json'}
    values = json.dumps(values)
    req = urllib2.Request(settings.GCM_SEND_MESSAGE_URL,values,headers)

    # Executing request
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        if e.code > 500: # Retrying request if GCM server is busy (using exponential back-off)

            sleep = e.getheader("Retry-After",str(wait)) # Honoring retry-after header
            if not sleep.isdigit():
                sleep = dt.datetime.strptime(e['retry-after'],'%a, %d %b %Y %H:%M:%S %Z')
                sleep = (timezone.now() - sleep).seconds
            else:
                sleep = int(sleep)

            # Retrying
            e89_push_messaging.push_tools.print_console('GCM server is busy. Retrying again in %d seconds.'%wait)
            time.sleep(wait)
            wait = wait*2
            return _do_post(registration_ids, data_dict,collapse_key,wait)
        else:
            _check_errors(e,registration_ids)

    return _check_errors(response,registration_ids)

def _check_errors(response,registration_ids):

    if (response.code == 400):
        raise AssertionError("Message could not be delivered to registration ids %s because the request could not be parsed as JSON. Values: %s."%(",".join(registration_ids)), str(values))
    elif (response.code == 401):
        raise AssertionError("Message could not be delivered to registration ids %s because there was an error authenticating the sender account. Check %s."%(",".join(registration_ids), "https://developer.android.com/google/gcm/http.html#auth_error"))

    json_response = response.read()
    json_response = json.loads(json_response)
    if json_response["failure"] != 0:
        Device = apps.get_model("e89_push_messaging", "Device")
        devices = Device.objects.filter(registration_id__in=registration_ids)
        logger = logging.getLogger("sentry")

        errors = {}
        for result,device in zip(json_response["results"],devices):
            if result.get("error"):
                errors[device.registration_id] = [result["error"],"owner_id: %d"%(device.owner.id)]

        logger.error( "It was not possible to process %s of %s GCM messages. Errors:%s"%( str(json_response["failure"]), str(len(registration_ids)), str(errors)) )

    return json_response["results"]