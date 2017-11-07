from django.db import models
from django.conf import settings

# Create your models here.
class Device(models.Model):
	PLATFORM_CHOICES = (("ios","iOS"),("android","Android"))
	owner = models.ForeignKey(settings.PUSH_DEVICE_OWNER_MODEL)
	registration_id = models.CharField(max_length = 200)
	platform = models.CharField(max_length=30,choices=PLATFORM_CHOICES)
	version = models.CharField(max_length=30, null=True)

	class Meta:
		unique_together = (("registration_id", "platform"),)
		ordering = [getattr(settings, 'PUSH_DEVICE_ORDERING', 'id')]

	def __unicode__(self):
		return '%s: %s - %s'%(self.platform,str(self.version), self.registration_id)