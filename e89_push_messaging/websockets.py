from django.conf import settings
from django.apps import apps
import e89_push_messaging.push_tools
import requests
import json

def send_message_websockets(owners, data_dict = {'type' : 'update'}):
	if e89_push_messaging.push_tools.is_id(owners[0]):
		OwnerModel = apps.get_model(settings.PUSH_DEVICE_OWNER_MODEL)
		owners = OwnerModel.objects.filter(id__in=owners).values_list(settings.PUSH_DEVICE_OWNER_IDENTIFIER, flat=True)
	else:
		owners = [e89_push_messaging.push_tools.deepgetattr(owner, settings.PUSH_DEVICE_OWNER_IDENTIFIER) for owner in owners]

	payload = {
		"identifiers": list(owners),
	}
	payload.update(data_dict)
	post_to_server(payload)

def post_to_server(data):
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	url = settings.PUSH_WEBSOCKET_URL
	requests.post(url,data=json.dumps(data), headers=headers)
