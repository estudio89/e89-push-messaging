# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.conf import settings
from django.apps import apps
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt

import e89_push_messaging.push_tools
import e89_security.tools
import json


@csrf_exempt
def register_device(request):
    ''' View para registro do device no Google Cloud Messaging. Deve ser chamada logo após a autenticação.
        Deve receber um json no formato:
        {
            "token":"aSDASdasd123!",
            "registration_id":"ASDasda!@d",
            "old_registration_id":"ASDasda!@d"
        }
    '''
    if request.method != 'POST':
        return HttpResponse("")

    json_obj = e89_security.tools._get_user_data(request, getattr(settings, "SYNC_ENCRYPTION_PASSWORD", ""), getattr(settings, "SYNC_ENCRYPTION", False))

    old_registration_id = json_obj.get('old_registration_id')
    registration_id = json_obj['registration_id']
    platform = json_obj['platform']

    Owner = apps.get_model(settings.PUSH_DEVICE_OWNER_MODEL)

    json_identifier = settings.PUSH_DEVICE_OWNER_IDENTIFIER.split('__')[-1]
    kwargs =  {settings.PUSH_DEVICE_OWNER_IDENTIFIER:json_obj[json_identifier]}
    owner = get_object_or_404(Owner,**kwargs)
    e89_push_messaging.push_tools.register_device(owner, registration_id, old_registration_id, platform)

    return e89_security.tools._generate_user_response({}, getattr(settings, "SYNC_ENCRYPTION_PASSWORD", ""), getattr(settings, "SYNC_ENCRYPTION", False))
