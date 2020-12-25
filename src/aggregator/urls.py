from django.conf.urls import url

from aggregator.views import ajax_plugin_configuration, StatsView

app_name = "aggregator"

urlpatterns = [
    url(r'^stats/', StatsView.as_view(), name='stats'),
]
