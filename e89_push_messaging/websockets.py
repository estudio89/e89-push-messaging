from django.conf import settings
from django.apps import apps
import e89_push_messaging.push_tools
import requests
import json

def send_message_websockets(owners, data_dict = {'type' : 'update'}):
	if type(owners[0]) == type(1):
		OwnerModel = apps.get_model(settings.PUSH_DEVICE_OWNER_MODEL)
		owners = OwnerModel.objects.filter(id__in=owners).values_list(settings.PUSH_DEVICE_OWNER_IDENTIFIER, flat=True)
	else:
		owners = [e89_push_messaging.push_tools.deepgetattr(owner, settings.PUSH_DEVICE_OWNER_IDENTIFIER) for owner in owners]

	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	url = settings.PUSH_WEBSOCKET_URL

	payload = {
		"identifiers": list(owners),
	}

	payload.update(data_dict)

	requests.post(url,data=json.dumps(payload), headers=headers)

