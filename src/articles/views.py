from datetime import timedelta

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.datetime_safe import date
from el_pagination.views import AjaxListView

from articles.models import Article


def login_vk_view(request):
    return render(request, 'registration/login.html', {})


class HomeView(AjaxListView):
    model = Article
    template_name = "articles/article_list.html"
    page_template = "articles/article_list_page.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        today = date.today()
        if today.isoweekday() == 7:
            css_hr_class = "divider-sunday"
        else:
            css_hr_class = "divider-weekday"

        context.update({
            "css_hr_class": css_hr_class,
            "active_lang": self.request.GET.get('language', ''),
        })

        return context

    def get_queryset(self):
        qs = super(HomeView, self).get_queryset()

        qs = qs.filter(timestamp__gte=timezone.now() - timedelta(days=7))

        qs = qs.exclude(
            Q(text=None) | Q(active=False)
        ).select_related('source', 'picture').order_by('-source_datetime')

        # Filters section
        language = self.request.GET.get('language', None)
        if language is not None:
            qs = qs.filter(language=language)

        source = self.request.GET.get('source', None)
        if source is not None and source.isnumeric():
            qs = qs.filter(source__id=int(source))

        return qs[:50]
