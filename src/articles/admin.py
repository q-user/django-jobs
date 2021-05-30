from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html
from import_export.admin import ImportExportMixin

from articles.models import Article
from articles.resources import ArticleResource


class ArticleAdmin(ImportExportMixin, ModelAdmin):
    list_display = ('active', 'title', 'source_datetime', 'source', 'article_url',)
    list_editable = ('active',)
    list_display_links = ['title', 'source_datetime']
    list_per_page = 20
    save_on_top = True
    ordering = ['-source_datetime']
    resource_class = ArticleResource

    # pylint: disable=no-self-use
    def article_url(self, obj):
        return format_html('<a href="%s" target="_blank">%s</a>' % (obj.url, obj.url))

    article_url.short_description = "Оригинал записи"


admin.site.register(Article, ArticleAdmin)
