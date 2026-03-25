from fastapi import status
import pytest

def test_files_with_multiple_special_rules(upload_file,update_last_accessed,auto_tiering,get_metadata):
    """
    This test covers:
    - Validation of files with multiple special rules applied to it.
    """
    # Upload a file which is eligible for both LEGAL and PRIORITY.
    upload_response = upload_file(size_mb = 1000 , filename = "LEGAL_PRIORITY_file.txt")
    assert upload_response.status_code == status.HTTP_201_CREATED

    # Get the file_id
    file_id = upload_response.json()['file_id']

    # Update last accessed, trigger auto-tiering.
    # It should remain in HOT tier as it is 29 days old
    update_last_accessed(file_id,29)
    auto_tiering()
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'HOT'

    # Update last accessed, trigger auto-tiering.
    # It should remain in HOT tier as it is 89 days old and has LEGAL and is Priority file.
    update_last_accessed(file_id,89)
    auto_tiering()
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'HOT'

    # Update last accessed, trigger auto-tiering.
    # It should remain in HOT tier as it is 180 days old and has LEGAL and is Priority file.
    update_last_accessed(file_id,180)
    auto_tiering()
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'HOT'

def test_files_in_all_tiers(upload_file,update_last_accessed,auto_tiering,get_metadata):
    """
    This test covers:
    - Validation of files in all tiers based on last accessed time.
    """
    # Upload three different files 
    upload_response1 = upload_file(size_mb = 1000 , filename = "file1.txt")
    upload_response2 = upload_file(size_mb = 800 , filename = "file2.txt")
    upload_response3 = upload_file(size_mb = 500 , filename = "file3.txt")

    # Get the file_ids
    file_id1 = upload_response1.json()['file_id']
    file_id2 = upload_response2.json()['file_id']
    file_id3 = upload_response3.json()['file_id']

    # Update last accessed for each file to place them in different tiers.
    update_last_accessed(file_id1,10)
    update_last_accessed(file_id2,40)
    update_last_accessed(file_id3,100)

    # Perform auto-tiering twice to ensure all files are moved to their respective tiers.
    auto_tiering()
    auto_tiering()

    # Get the metadata of all three files and validate their tiers.
    metadata1 = get_metadata(file_id1).json()
    metadata2 = get_metadata(file_id2).json()
    metadata3 = get_metadata(file_id3).json()

    assert metadata1['tier'] == 'HOT'
    assert metadata2['tier'] == 'WARM'
    assert metadata3['tier'] == 'COLD'   

@pytest.mark.parametrize("file_name",["!@#$%^&*)(","ab123","Hello"*100," "])
def test_upload_unusual_names(upload_file,file_name,validate_file_metadata):
    """
    This test covers:
    - Validation of file upload with unusual names like :
        - Names with special characters.
        - Very long names.
        - Names with only spaces.
    """
    # Create and upload files, validate the response and metadata.
    response = upload_file(filename=file_name)
    assert response.status_code == status.HTTP_201_CREATED
    validate_file_metadata(response.json())

def test_files_in_boundary_conditions(upload_file,update_last_accessed,auto_tiering,get_metadata):
    """
    This test covers:
    - Validation of files in boundary conditions for tier movement like:
        - A file which is exactly 30 days old should move to WARM tier.
        - A file which is exactly 90 days old should move to COLD tier.
    """
    # Upload three different files 
    upload_response = upload_file(size_mb = 1000 , filename = "file1.txt")

    # Get the file_ids
    file_id = upload_response.json()['file_id']

    # Update last accessed to 30 days
    update_last_accessed(file_id,30)

    # Perform auto-tiering.
    auto_tiering()

    # Get the metadata of files and validate their tiers.
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'WARM'

    # Update last accessed to 90 days
    update_last_accessed(file_id,90)
    auto_tiering()
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'COLD'

