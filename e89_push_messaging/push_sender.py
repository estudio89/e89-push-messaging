from django.conf import settings
from django.db.models import Q
from django.apps import apps
import e89_push_messaging.push_tools
import requests
import json

class PushSender(object):

	def __init__(self, platforms=['ios', 'android', 'ws']):
		self.platforms = platforms

	def get_sender(self, platform):
		if platform == 'ios':
			return iOSPushSender()
		elif platform == 'android':
			return AndroidPushSender()
		else:
			return WSPushSender()

	def send(self, **kwargs):
		for platform in self.platforms:
			Sender = self.get_sender(platform)
			Sender.send(**kwargs)

class AbstractPushSender(object):
	def _get_url(self):
		raise NotImplementedError()

	def _get_identifiers(self, owners):
		raise NotImplementedError()

	def _get_data(self, **kwargs):
		raise NotImplementedError()

	def send(self, **kwargs):
		''' Parameters:

				owners
				exclude_reg_ids=[]
				include_reg_ids=[]
				data_dict = {}
				collapse_key="update"
		'''

		identifiers = list(self._get_identifiers(**kwargs))
		if len(identifiers) == 0:
			return

		data = {
			"identifiers": identifiers
		}

		data.update(self._get_data(**kwargs))
		self.post_to_server(data)

	def post_to_server(self, data):
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		url = self._get_url()
		requests.post(url,data=json.dumps(data), headers=headers)

class MobilePushSender(AbstractPushSender):

	def _get_platform(self):
		raise NotImplementedError()

	def _get_identifiers(self, owners, exclude_reg_ids=[], include_reg_ids=[], **kwargs):
		if len(owners) == 0:
			return []

		# Looking for devices
		Device = apps.get_model("e89_push_messaging", "Device")

		# Verifying if owner id's were passed instead of reg id's
		if exclude_reg_ids and type(exclude_reg_ids[0]) == type(1):
		    exclude_reg_ids = Device.objects.filter(owner_id__in=exclude_reg_ids).values_list('registration_id',flat=True)

		if include_reg_ids and type(include_reg_ids[0]) == type(1):
		    include_reg_ids = Device.objects.filter(owner_id__in=include_reg_ids).values_list('registration_id',flat=True)

		devices = Device.objects.filter(Q(owner__in=owners) | Q(registration_id__in=include_reg_ids),Q(platform=self._get_platform()),~Q(registration_id__in=exclude_reg_ids)).distinct()
		registration_ids = list(devices.values_list("registration_id",flat=True))
		return registration_ids

class iOSPushSender(MobilePushSender):
	def _get_platform(self):
		return "ios"

	def _get_url(self):
		return (settings.PUSH_SERVER_URL + '/push/send/apns/').replace('//push', '/push')

	def _get_data(self, **kwargs):
		payload_alert = kwargs.pop("payload_alert", None)
		badge = 1 if payload_alert else None
		sound = "default" if payload_alert else None
		payload = kwargs.pop("data_dict", {'type':'update'})
		payload.update({"content-available":1})

		if settings.DEBUG:
			certFile = settings.APNS_DEV_CERTIFICATE
			keyFile = settings.APNS_DEV_KEY
		else:
			certFile = settings.APNS_PROD_CERTIFICATE
			keyFile = settings.APNS_PROD_KEY

		data = {
			"production": not settings.DEBUG,
			"certFile":certFile,
			"keyFile":keyFile,
			"payload":payload,
			"badge": badge,
			"sound": sound,
			"alert": payload_alert,
		}
		return data


class AndroidPushSender(MobilePushSender):
	def _get_platform(self):
		return "android"

	def _get_url(self):
		return (settings.PUSH_SERVER_URL + '/push/send/gcm/').replace('//push', '/push')

	def _get_data(self, **kwargs):
		payload = kwargs.pop("data_dict", {'type':'update'})
		collapse_key=kwargs.pop("collapse_key", "update")
		data = {
			"payload": payload,
			"collapseKey": collapse_key,
			"apiKey": settings.GCM_API_KEY
		}
		return data

class WSPushSender(AbstractPushSender):

	def _get_url(self):
		return (settings.PUSH_SERVER_URL + '/push/send/ws/').replace('//push', '/push')

	def _get_identifiers(self, owners, **kwargs):
		if len(owners) == 0:
			return []

		if type(owners[0]) == type(1):
			OwnerModel = apps.get_model(settings.PUSH_DEVICE_OWNER_MODEL)
			identifiers = OwnerModel.objects.filter(id__in=owners).values_list(settings.PUSH_DEVICE_OWNER_IDENTIFIER, flat=True)
		else:
			identifiers = [e89_push_messaging.push_tools.deepgetattr(owner, settings.PUSH_DEVICE_OWNER_IDENTIFIER) for owner in owners]

		return identifiers

	def _get_data(self, **kwargs):
		return kwargs.pop("data_dict", {'type':'update'})




