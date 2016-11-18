from django.conf.urls import url
import e89_push_messaging.views
urlpatterns = [
    url(r'^push_messaging/register-device/', e89_push_messaging.views.register_device),
    url(r'^push_messaging/(?P<platform>\w+)/process-results/', e89_push_messaging.views.process_results),
]

