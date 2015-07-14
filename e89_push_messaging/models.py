from django.db import models
from django.conf import settings

# Create your models here.
class Device(models.Model):
	PLATFORM_CHOICES = (("ios","iOS"),("android","Android"))
	owner = models.ForeignKey(settings.PUSH_DEVICE_OWNER_MODEL)
	registration_id = models.CharField(max_length = 200)
	platform = models.CharField(max_length=30,choices=PLATFORM_CHOICES)

	class Meta:
		unique_together = (("registration_id", "platform"),)

	def __unicode__(self):
		return '%s: %s'%(self.platform,self.registration_id)