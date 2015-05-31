from django.conf.urls import patterns, include, url

urlpatterns = patterns('e89_push_messaging.views',

    (r'^push_messaging/register-device/', 'register_device'),
)

