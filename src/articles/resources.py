from import_export.resources import ModelResource

from articles.models import Article


class ArticleResource(ModelResource):
    class Meta:
        model = Article
        skip_unchanged = True
        report_skipped = False
