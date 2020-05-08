import os
from unittest import mock

import dropbox
from django.test import TestCase, tag, override_settings
from dropbox.exceptions import ApiError

from aggregator.tests.factories import DataSourceFactory
from articles.tasks import export_datasets, dropbox_file
from articles.tests.factories import ArticleFactory


class ExportDatasetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.articles = ArticleFactory.create_batch(1)
        cls.data_sources = DataSourceFactory.create_batch(1)

    @mock.patch('articles.tasks.open', new_callable=mock.mock_open)
    def test_export_datasets_writes_files(self, mock_open):
        if os.path.exists('/tmp/datasources.json'):
            os.unlink('/tmp/datasources.json')
        if os.path.exists('/tmp/articles.csv'):
            os.unlink('/tmp/articles.csv')

        export_datasets()

        os.path.exists('/tmp/datasources.json')
        os.path.exists('/tmp/articles.csv')


@tag('task')
@override_settings(DROPBOX_TOKEN="123")
@mock.patch('os.path.getsize')
@mock.patch('articles.tasks.open', new=mock.mock_open(read_data="line1, line2"), create=True)
@mock.patch.object(dropbox.Dropbox, 'files_get_metadata')
@mock.patch.object(dropbox.Dropbox, 'files_upload')
class DropboxFileTest(TestCase):
    def test_dropbox_file_uploads_new_file_if_there_is_no_in_dropbox(
            self,
            files_upload_mock,
            files_get_metadata_mock,
            getsize_mock,

    ):
        files_get_metadata_mock.side_effect = ApiError(123, 'not_found', 'qwerty', '234')
        getsize_mock.return_value = 101
        dropbox_file("filename")
        self.assertTrue(files_upload_mock.assert_called)

    def test_dropbox_file_uploads_new_file_if_it_is_bigger_than_existing_one(
            self,
            files_upload_mock,
            files_get_metadata_mock,
            getsize_mock,
    ):
        class DPXMetadataMock():
            size = 100

        metadata = DPXMetadataMock()
        files_get_metadata_mock.return_value = metadata
        getsize_mock.return_value = 101
        dropbox_file("filename")
        self.assertTrue(files_upload_mock.called)
