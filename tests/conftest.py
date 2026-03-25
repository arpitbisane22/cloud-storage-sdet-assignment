import pytest
import io
from fastapi.testclient import TestClient
from src.storage_service import app, files_metadata, files_content


@pytest.fixture
def client():
    """Shared HTTP client for all tests"""
    return TestClient(app)

@pytest.fixture
def create_file():
    """It will create an x MB file."""
    def _create_file(x):
        return io.BytesIO(b"x" * int(x * 1024 * 1024))
    return _create_file

@pytest.fixture
def upload_file(client, create_file):    
    """It will upload a file and return the metadata"""
    def _upload_file(size_mb=2,filename="text.txt"):
        return client.post("/files", files={"file": (filename, create_file(size_mb))})
    return _upload_file

@pytest.fixture
def download_file(client):
    """It will download a file using file_id"""
    def _download_file(file_id):
        return client.get(f"/files/{file_id}")
    return _download_file

@pytest.fixture
def get_metadata(client):
    """It will get the metadata of a file using file_id"""
    def _get_metadata(file_id):
        return client.get(f"/files/{file_id}/metadata")
    return _get_metadata

@pytest.fixture
def delete_file(client):
    """It will delete a file using file_id"""
    def _delete_file(file_id):
        return client.delete(f"/files/{file_id}")
    return _delete_file

@pytest.fixture
def validate_file_metadata():
    """It will validate the file metadata"""
    def _validate(metadata):
        assert "file_id" in metadata
        assert "filename" in metadata
        assert "size" in metadata
        assert "tier" in metadata
        assert "created_at" in metadata
        assert "last_accessed" in metadata
        assert "content_type" in metadata
        assert "etag" in metadata
    return _validate

@pytest.fixture
def update_last_accessed(client):
    """It will update the last accessed time of a file using file_id and days_ago"""
    def _update(file_id, days_ago):
        return client.post(f"/admin/files/{file_id}/update-last-accessed",json={"days_ago": days_ago})
    return _update

@pytest.fixture
def auto_tiering(client):
    """It will trigger the auto-tiering process"""
    def _tiering():
        return client.post("/admin/tiering/run")
    return _tiering

@pytest.fixture
def get_stats(client):
    """It will get the stats of the storage system"""
    def _stats():
        return client.get("/admin/stats")
    return _stats


@pytest.fixture(autouse=True,scope='module')
def cleanup_storage():
    files_metadata.clear()
    files_content.clear()
    yield
    files_metadata.clear()
    files_content.clear()