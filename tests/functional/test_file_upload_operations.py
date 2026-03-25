from fastapi import status
import pytest

@pytest.mark.parametrize("size_mb, filenames", [ (1, "file1.txt"), (5, "file2.txt"), (10, "!@#$"), (50, "LEGAL_1234"), (100, "file5_PRIORITY_.txt"), (500, " "), (10000, ".txt"), (6.5, "Lucidity"*100) ])
def test_upload_file_with_various_sizes_and_filenames(upload_file, validate_file_metadata, size_mb,filenames):
    """
    This test covers :
    - Files of various sizes.
    - Files with different types of names, including special characters, legal priority indicators.
    """
    
    # Create and Upload a file
    response = upload_file(size_mb , filename = filenames)

    # Validate the response and metadata
    validate_file_metadata(response.json())

    # Assert the response status and tier
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["tier"] == "HOT"

@pytest.mark.parametrize("size_mb",[0, 0.5, 0.99, 10241])  # 0.5MB and 10GB
def test_upload_file_with_invalid_size(upload_file, size_mb):
    """
    This test covers:
    - Attempting to upload files with invalid sizes, as only files between 1MB and 10GB are supported.
    """
    # Create and Upload a file with invalid size
    response = upload_file(size_mb)

    # Validate the reponse,it must return 400
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.parametrize("file_name",["LEGAL_456","_PRIORITY_file.txt","LEGAL_PRIORITY_file","xyz_PRIORITY_"])
def test_upload_file_with_special_names(upload_file,file_name,validate_file_metadata):
    """
    This test covers:
    - Uploading files with special names.
    - Includes : legal priority indicators.
    """
    # Create and Upload a file with special name
    response = upload_file(filename=file_name)

    # Validate the response and metadata
    assert response.status_code == status.HTTP_201_CREATED
    validate_file_metadata(response.json())




