# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.conf import settings
from django.apps import apps
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt

import json
import e89_push_messaging.push_tools

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
    if request.method == 'POST':
        try:
            json_obj = json.loads(request.body)
        except ValueError:
            json_obj = json.loads(request.POST['json'])

        registration_id = json_obj['registration_id']
        platform = json_obj['platform']
        json_identifier = settings.PUSH_DEVICE_OWNER_IDENTIFIER.split('__')[-1]
        kwargs =  {settings.PUSH_DEVICE_OWNER_IDENTIFIER:json_obj[json_identifier]}
        app,model = settings.PUSH_DEVICE_OWNER_MODEL.split('.')
        Owner = apps.get_model(app, model)

        owner = get_object_or_404(Owner,**kwargs)
        e89_push_messaging.push_tools.register_device(owner, registration_id, platform)
    return HttpResponse('{}',content_type="application/json; charset=utf-8")
