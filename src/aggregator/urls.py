from django.conf.urls import url

from aggregator.views import ajax_plugin_configuration, StatsView

app_name = "aggregator"

urlpatterns = [
    url(r'^ajax/plugin-configuration', ajax_plugin_configuration, name='ajax-configuration'),
    url(r'^stats/', StatsView.as_view(), name='stats'),
]
