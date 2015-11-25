from django.conf import settings
from django.db.models import Q
from django.apps import apps
from django.core.urlresolvers import reverse
from django.apps import apps
import e89_push_messaging.push_tools
import e89_push_messaging.views
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
			Sender.send(platform=platform, **kwargs)

	def process_response(self, platform, response):
		Sender = self.get_sender(platform)
		Sender.process_response(response)

class AbstractPushSender(object):
	def _get_url(self):
		raise NotImplementedError()

	def _get_identifiers(self, owners):
		raise NotImplementedError()

	def _get_data(self, **kwargs):
		raise NotImplementedError()

	def send(self, platform, **kwargs):
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
		self.post_to_server(data, platform)

	def post_to_server(self, data, platform):
		from urlparse import urlparse
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		domain = urlparse(settings.WEBSITE_DOMAIN)

		data["processResponse"] = {
			"host": domain.hostname,
			"port": domain.port if domain.port is not None else "80",
			"path": reverse(e89_push_messaging.views.process_results, kwargs={"platform":platform})
		}
		url = self._get_url()
		requests.post(url,data=json.dumps(data), headers=headers)

	def process_response(self, data):
		pass

class MobilePushSender(AbstractPushSender):

	def _get_platform(self):
		raise NotImplementedError()

	def _get_identifiers(self, owners, exclude_reg_ids=[], include_reg_ids=[], **kwargs):
		if len(owners) == 0:
			return []

		# Looking for devices
		Device = apps.get_model("e89_push_messaging", "Device")

		# Verifying if owner id's were passed instead of reg id's
		if exclude_reg_ids and e89_push_messaging.push_tools.is_id(exclude_reg_ids[0]):
		    exclude_reg_ids = Device.objects.filter(owner_id__in=exclude_reg_ids).values_list('registration_id',flat=True)

		if include_reg_ids and e89_push_messaging.push_tools.is_id(include_reg_ids[0]):
		    include_reg_ids = Device.objects.filter(owner_id__in=include_reg_ids).values_list('registration_id',flat=True)

		devices = Device.objects.filter(Q(owner__in=owners) | Q(registration_id__in=include_reg_ids),Q(platform=self._get_platform()),~Q(registration_id__in=exclude_reg_ids)).distinct()
		registration_ids = list(devices.values_list("registration_id",flat=True))
		return registration_ids

	def process_response(self, data):
		Device = apps.get_model('e89_push_messaging','Device')
		toDelete = data.get("toDelete", [])

		Device.objects.filter(registration_id__in=toDelete).delete()
		for toChange in data.get("shouldChange",[]):
			dev = Device.objects.filter(registration_id=toChange["old"]).first()
			if dev is not None and not Device.objects.filter(registration_id=toChange["new"]).exists():
				dev.registration_id = toChange["new"]
				dev.save()

class iOSPushSender(MobilePushSender):
	def _get_platform(self):
		return "ios"

	def _get_url(self):
		return (settings.PUSH_SERVER_INTERNAL_URL + '/push/send/apns/').replace('//push', '/push')

	def _get_identifiers(self, owners, exclude_reg_ids=[], include_reg_ids=[], **kwargs):
		'''
			PARAMS:
				- get_ignored_owners: The boolean kwarg "get_ignored_owners" is used internally in order to know if the identifiers that
				are being fetched are only from the owners that should be ignored when sending a payload alert.

				This is used when sending a separate push message only to the owners that should not get a payload_alert.

				- owners_ignore_payload: this should always be a list. It contains owner ids that should not receive a payload alert.

				- payload_alert: String or None. This is the string that will be sent in the push alert text.'''

		get_ignored_owners = kwargs.pop("get_ignored_owners", False)
		owners_ignore_payload = kwargs.pop("owners_ignore_payload", [])
		payload_alert = kwargs.pop("payload_alert", None)
		exclude_reg_ids = exclude_reg_ids[:]
		if not get_ignored_owners:
			if len(owners_ignore_payload) > 0 and payload_alert:
				exclude_reg_ids.extend(owners_ignore_payload)

			return super(iOSPushSender, self)._get_identifiers(owners, exclude_reg_ids, include_reg_ids, **kwargs)
		else:
			owners = owners_ignore_payload
			return super(iOSPushSender, self)._get_identifiers(owners, exclude_reg_ids=[], include_reg_ids=[], **kwargs)

	def _get_data(self, **kwargs):
		payload_alert = kwargs.pop("payload_alert", None)
		badge = 1 if payload_alert else None
		sound = "default" if payload_alert else None
		payload = kwargs.pop("data_dict", {'type':'update'})

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


	def send(self, **kwargs):

		# First time: sending to everyone that should receive a payload alert
		super(iOSPushSender, self).send(**kwargs)

		# Second time: sending to everyone that should not receive a payload alert
		owners_ignore_payload = kwargs.get("owners_ignore_payload", [])
		payload_alert = kwargs.pop("payload_alert", None)
		if len(owners_ignore_payload) > 0 and payload_alert:
			kwargs["payload_alert"] = None
			kwargs["get_ignored_owners"] = True
			super(iOSPushSender, self).send(**kwargs)


class AndroidPushSender(MobilePushSender):
	def _get_platform(self):
		return "android"

	def _get_url(self):
		return (settings.PUSH_SERVER_INTERNAL_URL + '/push/send/gcm/').replace('//push', '/push')

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
		return (settings.PUSH_SERVER_INTERNAL_URL + '/push/send/ws/').replace('//push', '/push')

	def _get_identifiers(self, owners, exclude_reg_ids=[], include_reg_ids=[], **kwargs):

		if len(owners) == 0 and len(include_reg_ids) == 0:
			return []

		owners = list(owners)
		if e89_push_messaging.push_tools.is_id(owners[0]):
			OwnerModel = apps.get_model(settings.PUSH_DEVICE_OWNER_MODEL)

			owner_ids = list(owners)
			if len(include_reg_ids) > 0 and e89_push_messaging.push_tools.is_id(include_reg_ids[0]):
				owner_ids += list(include_reg_ids)

			if len(exclude_reg_ids) >0 and (type(exclude_reg_ids[0]) == type(u'') or type(exclude_reg_ids[0]) == type('')):
				exclude_reg_ids = []

			identifiers = OwnerModel.objects.filter(id__in=owner_ids).exclude(id__in=exclude_reg_ids).values_list(settings.PUSH_DEVICE_OWNER_IDENTIFIER, flat=True)
		else:
			if len(include_reg_ids) > 0 and e89_push_messaging.push_tools.is_id(include_reg_ids[0]):
				OwnerModel = apps.get_model(settings.PUSH_DEVICE_OWNER_MODEL)
				more_owners = OwnerModel.objects.filter(id__in=include_reg_ids)
				owners += list(more_owners)
			identifiers = [e89_push_messaging.push_tools.deepgetattr(owner, settings.PUSH_DEVICE_OWNER_IDENTIFIER) for owner in owners]

		return identifiers

	def _get_data(self, **kwargs):
		return kwargs.pop("data_dict", {'type':'update'})




