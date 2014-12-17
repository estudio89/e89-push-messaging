from django.conf.urls import patterns, include, url

urlpatterns = patterns('e89_push_messaging.views',
    #----------Admin----------
    (r'^push_messaging/register-device/', 'register_device'),
)

