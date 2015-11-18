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
@e89_security.tools.secure_view(encryption_key=getattr(settings, "SYNC_ENCRYPTION_PASSWORD", ""), encryption_active=getattr(settings, "SYNC_ENCRYPTION", False))
def register_device(request, data):
    ''' View para registro do device no Google Cloud Messaging. Deve ser chamada logo após a autenticação.
        Deve receber um json no formato:
        {
            "token":"aSDASdasd123!",
            "registration_id":"ASDasda!@d",
            "old_registration_id":"ASDasda!@d"
        }
    '''

    old_registration_id = data.get('old_registration_id')
    registration_id = data['registration_id']
    platform = data['platform']
    app_version = data.get('app_version')

    Owner = apps.get_model(settings.PUSH_DEVICE_OWNER_MODEL)

    json_identifier = settings.PUSH_DEVICE_OWNER_IDENTIFIER.split('__')[-1]
    kwargs =  {settings.PUSH_DEVICE_OWNER_IDENTIFIER:data[json_identifier]}
    owner = get_object_or_404(Owner,**kwargs)
    e89_push_messaging.push_tools.register_device(owner, registration_id, old_registration_id, platform, app_version)

    return {}
