from fastapi import status
from concurrent.futures import ThreadPoolExecutor

def test_consecutive_upload_download_and_deletes(upload_file, delete_file,get_stats,download_file):
    """
    This test covers:
    - Validation of consecutive upload, download, and delete operations.
    """
    # Initialize a list to store responses of upload operations.
    responses = []

    # Perform 500 consecutive uploads and store the responses.
    for i in range(500):
        response = upload_file(size_mb=10, filename=f"file_{i}.txt")
        responses.append(response)

    # Validate the responses of upload operations and ensure all files are created.
    for response in responses:
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['tier'] == 'HOT'

    # Get stats and validate total files count after uploads.
    stats = get_stats().json()
    assert stats['total_files'] == 500

    # Perform consecutive downloads for all uploaded files and validate the responses.
    for response in responses:
        download_response = download_file(response.json()['file_id'])
        assert download_response.status_code == status.HTTP_200_OK
        assert download_response.json()['filename'] == response.json()['filename']

    # Perform consecutive deletes for all uploaded files and validate the responses.
    for response in responses:
        delete_response = delete_file(response.json()['file_id'])
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Get stats and validate total files count after deletions.
    stats = get_stats().json()
    assert stats['total_files'] == 0

    
def test_concurrent_tiering(upload_file,update_last_accessed,auto_tiering,get_metadata,delete_file,get_stats):
    """
    This test covers:
    - Validation of concurrent tiering operations.
    """
    # Initialize a list to store responses of upload operations.
    responses = []

    # Upload 100 files consecutively and store the responses.
    for i in range(100):
        response = upload_file(size_mb=10, filename=f"file_{i}.txt")
        responses.append(response)

    # Validate the responses of upload operations and ensure all files are created in HOT tier.
    for response in responses:
        assert response.status_code == status.HTTP_201_CREATED

    # Get responses and update last accessed time to 31 days for all files.
    for response in responses:
        file_id = response.json()['file_id']
        update_last_accessed(file_id, 31)

    # Trigger auto-tiering operation. And validate movement from HOT to WARM tier.
    auto_tiering()
    for response in responses:
        file_id = response.json()['file_id']
        metadata = get_metadata(file_id).json()
        assert metadata['tier'] == 'WARM'

    # Get stats and validate total files count and count in each tier after first tiering.
    stats = get_stats().json()
    assert stats['total_files'] == 100
    assert stats['tiers']['HOT']['count'] == 0
    assert stats['tiers']['WARM']['count'] == 100

    # Update last accessed time to 91 days for all files.
    for response in responses:
        file_id = response.json()['file_id']
        update_last_accessed(file_id, 91)

    # Perform auto-tiering operation again. And validate movement from WARM to COLD tier.
    auto_tiering()
    for response in responses:
        file_id = response.json()['file_id']
        metadata = get_metadata(file_id).json()
        assert metadata['tier'] == 'COLD'

    # Get stats and validate total files count and count in each tier after second tiering.
    stats = get_stats().json()
    assert stats['total_files'] == 100
    assert stats['tiers']['HOT']['count'] == 0
    assert stats['tiers']['WARM']['count'] == 0
    assert stats['tiers']['COLD']['count'] == 100

    # Delete all files and validate the responses.
    for response in responses:
        delete_response = delete_file(response.json()['file_id'])
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Get stats and validate total files count after deletions.
    stats = get_stats().json()
    assert stats['total_files'] == 0
    

def test_concurrent_uploads_downloads_and_deletes(upload_file, delete_file,download_file,get_stats):
    """
    This test covers:
    - Validation of concurrent uploads, downloads, and deletes.
    """
    # Initialize a list to store responses of upload operations.
    responses = []
    
    # Method to perform upload operation, which will be used for concurrent execution.
    def upload(i):
        return upload_file(size_mb=2, filename=f"file_{i}")

    # Concurrently perform 100 uploads and store the responses.
    with ThreadPoolExecutor(max_workers=100) as executor:
        # Map the upload function to a range of 100 to perform concurrent uploads.
        results = executor.map(upload, range(100))
        for response in results:
            responses.append(response)

    # Validate responses
    for response in responses:
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['tier'] == 'HOT'

    # Get stats and validate total files count after uploads.
    stats = get_stats().json()  
    assert stats['total_files'] == 100

    # Concurrently download files
    def download(file_id):
        return download_file(file_id) 

    # Use ThreadPoolExecutor to perform concurrent downloads for all uploaded files and validate the responses.
    with ThreadPoolExecutor(max_workers=100) as executor:
        download_results = executor.map(download, [res.json()['file_id'] for res in responses])
        for download_response in download_results:
            assert download_response.status_code == status.HTTP_200_OK

    # Method to perform delete operation, which will be used for concurrent execution.
    def delete(file_id):
        return delete_file(file_id)        

    # Use ThreadPoolExecutor to perform concurrent deletes for all uploaded files and validate the responses.
    with ThreadPoolExecutor(max_workers=100) as executor:
        delete_results = executor.map(delete, [res.json()['file_id'] for res in responses])
        for delete_response in delete_results:
            assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # Get stats and validate total files count after deletions.
    stats = get_stats().json()
    assert stats['total_files'] == 0