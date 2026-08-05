"""Smoke test for the production GCS storage backend.

securedrop/settings/production.py wires up django-storages' GoogleCloudStorage
with a specific set of options (location=GS_MEDIA_PATH, default_acl="publicRead").
This exercises that exact configuration through the real django-storages code
and against the real google.cloud.storage.{Client,Bucket,Blob} classes (via
autospec, so a renamed/removed method or changed signature in a
google-cloud-storage upgrade fails loudly here) while faking out the network
calls those classes would otherwise make.
"""

from unittest import mock

from django.core.files.base import ContentFile
from django.test import SimpleTestCase

from google.cloud.storage import Blob, Bucket
from storages.backends.gcloud import GoogleCloudStorage


class FakeGCSBucket:
    """In-memory stand-in for the objects a real GCS bucket would hold."""

    def __init__(self):
        self.objects = {}


def _make_blob_mock(name, store):
    """Autospec'd Blob whose upload/download are backed by ``store``."""
    blob = mock.create_autospec(Blob, instance=True)
    blob.name = name
    blob.public_url = f"https://storage.googleapis.com/test-bucket/{name}"

    def upload_from_file(file_obj, rewind=False, **kwargs):
        if rewind:
            file_obj.seek(0)
        store.objects[name] = file_obj.read()

    def download_to_file(file_obj, **kwargs):
        file_obj.write(store.objects[name])

    blob.upload_from_file.side_effect = upload_from_file
    blob.download_to_file.side_effect = download_to_file
    if name in store.objects:
        blob.size = len(store.objects[name])
    return blob


def _make_bucket_mock(store):
    bucket = mock.create_autospec(Bucket, instance=True)

    def get_blob(name, chunk_size=None, **kwargs):
        if name not in store.objects:
            return None
        return _make_blob_mock(name, store)

    def blob_method(name, chunk_size=None, **kwargs):
        return _make_blob_mock(name, store)

    def delete_blob(name, retry=None, **kwargs):
        store.objects.pop(name, None)

    bucket.get_blob.side_effect = get_blob
    bucket.blob.side_effect = blob_method
    bucket.delete_blob.side_effect = delete_blob
    return bucket


class GoogleCloudStorageSmokeTest(SimpleTestCase):
    """Replicates the storage.save/open/exists/url/delete calls our app
    makes against default_storage, using the same GoogleCloudStorage
    options as securedrop/settings/production.py."""

    def setUp(self):
        self.store = FakeGCSBucket()
        bucket_mock = _make_bucket_mock(self.store)

        client_patcher = mock.patch("storages.backends.gcloud.Client", autospec=True)
        blob_patcher = mock.patch("storages.backends.gcloud.Blob", autospec=True)
        mock_client_cls = client_patcher.start()
        mock_blob_cls = blob_patcher.start()
        self.addCleanup(client_patcher.stop)
        self.addCleanup(blob_patcher.stop)

        mock_client_cls.return_value.bucket.return_value = bucket_mock
        mock_blob_cls.side_effect = lambda name, bucket, chunk_size=None: (
            _make_blob_mock(name, self.store)
        )

        # Same OPTIONS as STORAGES["default"] in securedrop/settings/production.py
        self.storage = GoogleCloudStorage(
            bucket_name="test-bucket",
            project_id="test-project",
            credentials=mock.Mock(),
            location="media",
            default_acl="publicRead",
        )

    def test_save_read_exists_url_delete_round_trip(self):
        content = b"hello from a smoke test"
        name = self.storage.save("uploads/example.txt", ContentFile(content))

        self.assertTrue(self.storage.exists(name))

        with self.storage.open(name, "rb") as f:
            self.assertEqual(f.read(), content)

        url = self.storage.url(name)
        self.assertIn("test-bucket", url)
        self.assertIn(name, url)

        self.storage.delete(name)
        self.assertFalse(self.storage.exists(name))

    def test_missing_file_does_not_exist(self):
        self.assertFalse(self.storage.exists("uploads/does-not-exist.txt"))
