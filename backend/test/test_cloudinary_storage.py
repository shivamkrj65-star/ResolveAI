import asyncio
import io

import pytest
from fastapi import UploadFile

from app.core.config import Settings, settings
from app.services.cloudinary_service import CloudinaryStorageError, CloudinaryStorageService as Storage
from app.services.image_processing_service import ImageProcessingService
from test_api import _evidence_bytes


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setattr(settings, 'CLOUDINARY_URL', '')
    monkeypatch.setattr(settings, 'CLOUDINARY_CLOUD_NAME', 'test-cloud')
    monkeypatch.setattr(settings, 'CLOUDINARY_API_KEY', 'test-key')
    monkeypatch.setattr(settings, 'CLOUDINARY_API_SECRET', 'test-secret')


def prepared():
    return asyncio.run(ImageProcessingService.prepare_upload(UploadFile(filename='evidence.jpg', file=io.BytesIO(_evidence_bytes()))))


def test_settings_have_no_embedded_credentials(monkeypatch):
    for name in ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET', 'CLOUDINARY_URL']:
        monkeypatch.delenv(name, raising=False)
        assert getattr(Settings(), name) == ''


def test_url_credentials_are_parsed_and_passed_to_sdk(monkeypatch):
    import cloudinary.uploader
    monkeypatch.setattr(settings, 'CLOUDINARY_URL', ' "cloudinary://url-key:encoded%2Bsecret@url-cloud" ')
    calls = []
    def upload(file, **options):
        calls.append(options)
        return {'public_id': options['public_id'], 'secure_url': 'https://res.cloudinary.com/url-cloud/image/upload/evidence.jpg', 'version': 42}
    monkeypatch.setattr(cloudinary.uploader, 'upload', upload)
    result = asyncio.run(Storage.upload_images('case_test', [prepared()]))
    assert calls[0]['api_key'] == 'url-key'
    assert calls[0]['api_secret'] == 'encoded+secret'
    assert calls[0]['cloud_name'] == 'url-cloud'
    assert '/url-cloud/' in result[0].thumbnail_url
    assert result[0].secure_url.startswith('https://')


@pytest.mark.parametrize('url', ['https://key:secret@cloud', 'cloudinary://cloud', 'not-a-url'])
def test_invalid_url_fails_without_exposing_secret(monkeypatch, url):
    monkeypatch.setattr(settings, 'CLOUDINARY_URL', url)
    assert not Storage.is_configured()
    with pytest.raises(CloudinaryStorageError, match='Invalid CLOUDINARY_URL'):
        asyncio.run(Storage.upload_images('case_test', [prepared()]))


def test_partial_batch_failure_rolls_back_and_does_not_embed_images(monkeypatch):
    import cloudinary.uploader
    calls, deleted = [], []
    def upload(file, **options):
        calls.append(options)
        if len(calls) == 2:
            raise RuntimeError('Invalid API key PRIVATE_VALUE')
        return {'public_id': options['public_id'], 'secure_url': 'https://example.invalid/evidence.jpg'}
    monkeypatch.setattr(cloudinary.uploader, 'upload', upload)
    monkeypatch.setattr(cloudinary.uploader, 'destroy', lambda public_id, **options: deleted.append(public_id) or {'result': 'ok'})
    with pytest.raises(CloudinaryStorageError) as error:
        asyncio.run(Storage.upload_images('case_test', [prepared(), prepared()]))
    assert 'PRIVATE_VALUE' not in str(error.value)
    assert 'credentials' in str(error.value)
    assert deleted == [calls[0]['public_id']]
    assert len(calls) == 2  # No fallback account or retry with embedded secrets.


def test_failed_delete_is_not_reported_as_success(monkeypatch):
    import cloudinary.uploader
    from types import SimpleNamespace
    monkeypatch.setattr(cloudinary.uploader, 'destroy', lambda *args, **kwargs: {'result': 'error'})
    with pytest.raises(CloudinaryStorageError, match='retained'):
        asyncio.run(Storage.delete_images([SimpleNamespace(secure_url='https://example.invalid/x', public_id='x')]))
