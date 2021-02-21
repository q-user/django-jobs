from django.conf.urls import url

from aggregator.views import StatsView

app_name = "aggregator"

urlpatterns = [
    url(r'^stats/', StatsView.as_view(), name='stats'),
]
