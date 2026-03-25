from fastapi import status

def test_download_file(upload_file,download_file):
    """
    This test covers:
    - Validation of successful file download operation.
    """
    # Create and Upload a new file. Validate status code.
    upload_response = upload_file(size_mb = 1000 , filename = "abcd.txt")
    assert upload_response.status_code == status.HTTP_201_CREATED

    # Call download endpoint to download file and validate the response.
    download_response = download_file(upload_response.json()['file_id'])
    assert download_response.json()['filename'] == upload_response.json()['filename']

    # Validate the content and content_type in response.
    assert download_response.json()['content'] != None
    assert 'content_type' in download_response.json()

def test_download_invalid_file(download_file):
    """ This test covers:
    - Validation of download operation with invalid file_id.
    """
    # Try to download a file which doesn't exist. Validate the status code.
    download_response = download_file(" ")
    assert download_response.status_code == status.HTTP_404_NOT_FOUND

def test_last_access_updation_after_download(download_file,upload_file,get_metadata):
    """ This test covers:
    - Validation of last_accessed updation after a successful download operation.
    """
    # Upload a new file and validate the status code.
    upload_response = upload_file(size_mb = 2000 , filename = "abcd.txt")
    assert upload_response.status_code == status.HTTP_201_CREATED

    # Fetch the time of creation of file and last accessed, it should be same.
    created_at = upload_response.json()['created_at']
    last_accessed = upload_response.json()['last_accessed']
    assert created_at == last_accessed

    # Download the file and fetch the metadata of file. 
    # Validate last_accessed time should be greater than created_at time.
    download_response = download_file(upload_response.json()['file_id'])
    metadata = get_metadata(upload_response.json()['file_id'])
    assert metadata.json()['last_accessed'] > created_at

def test_download_deleted_file(download_file,upload_file,delete_file):
    """
    This test covers:
    - Validation of download operation with a deleted file.
    """
    # Upload a new file and validate the status code.
    upload_response = upload_file(size_mb = 3000 , filename = "abcd.txt")
    assert upload_response.status_code == status.HTTP_201_CREATED

    # Delete the file
    delete_file(upload_response.json()['file_id'])

    # Try to download the deleted file, it should return 404 Not Found.
    download_response = download_file(upload_response.json()['file_id'])
    assert download_response.status_code == status.HTTP_404_NOT_FOUND







        