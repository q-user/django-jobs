from datetime import date, timedelta

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Max
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils.module_loading import import_string
from django.views.generic import TemplateView

from aggregator.models import DataSource


def ajax_plugin_configuration(request):
    if not request.is_ajax():
        raise PermissionDenied
    plugin_path = request.POST.get('plugin', None)
    if not plugin_path:
        return JsonResponse({'error': 'plugin field required'})
    Plugin = import_string(plugin_path)
    return JsonResponse(Plugin.configuration)


class StatsView(TemplateView):
    template_name = "aggregator/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        week_delta = date.today() - timedelta(days=7)
        sources = DataSource.objects.annotate(
            week_count=Count('articles',
                             filter=Q(articles__timestamp__gte=week_delta)),
            total_count=Count('articles'),
            newest_article_time=Coalesce(Max('articles__timestamp'),
                                         date(1, 1, 1))
        ).order_by('-newest_article_time')

        context.update({
            "data_sources": sources
        })
        return context
