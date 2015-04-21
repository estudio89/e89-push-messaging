import e89_push_messaging.push_tools
from django.apps import apps
from django.conf import settings

def recover_files(owner_ids=[]):
	app,model = settings.PUSH_DEVICE_OWNER_MODEL.split('.')
	Owner = apps.get_model(app,model)
	owners = Owner.objects.filter(id__in=owner_ids)
	e89_push_messaging.push_tools.send_message(owners, data_dict={'type':'recovery','server':settings.PUSH_FTP_SERVER,'username':settings.PUSH_FTP_USER, 'password':settings.PUSH_FTP_PASSWORD,'path':settings.PUSH_FTP_FOLDER},collapse_key="recovery")