from fastapi import status

def test_delete_existing_file(upload_file,delete_file,get_metadata):
    """
    This test covers:
    - Validation of successful file deletion operation.
    """
    # Create and Upload a new file. Validate status code.
    upload_response = upload_file(size_mb = 1000 , filename = "abcd.txt")
    assert upload_response.status_code == status.HTTP_201_CREATED

    # Get the file_id from response and delete the file. Validate the status code.
    delete_response = delete_file(upload_response.json()['file_id'])
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Try to get the metadata of deleted file, it should return 404 Not Found.
    metadata = get_metadata(upload_response.json()['file_id'])
    assert metadata.status_code == status.HTTP_404_NOT_FOUND

def test_delete_invalid_file(delete_file):
    """
    This test covers:
    - Validation of file deletion operation with invalid file_id.
    """
    # Try to delete a file which doesn't exist. Validate the status code.
    delete_response = delete_file(file_id = " ")
    assert delete_response.status_code == status.HTTP_404_NOT_FOUND




