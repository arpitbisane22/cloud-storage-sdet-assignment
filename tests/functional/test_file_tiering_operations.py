from fastapi import status
import pytest

def test_movement_from_HOT_to_WARM(upload_file,update_last_accessed,auto_tiering,get_metadata,delete_file):
    """
    This test covers:
    - Movement of files from HOT to WARM tier after 30 days of inactivity.
    """
    # Create and Upload a file
    upload_response = upload_file(size_mb = 1000 , filename = "abcd.txt")

    # Validate the response and tier
    assert upload_response.status_code == status.HTTP_201_CREATED
    assert upload_response.json()['tier'] == 'HOT'

    # Get the file_id and update last accessed to 31 days ago
    file_id = upload_response.json()['file_id']
    update_last_accessed(file_id,31)

    # Trigger auto-tiering
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 1

    # Validate the tier movement to WARM
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'WARM'

    # Delete the file
    delete_response = delete_file(file_id)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

def test_movement_from_HOT_to_WARM_to_COLD(upload_file,update_last_accessed,auto_tiering,get_metadata,delete_file):
    """
    This test covers:
    - Movement of files from HOT to WARM tier after 31 days of inactivity.
    - Movement of files from WARM to COLD tier after 91 days of inactivity.
    """

    # Create and Upload a file and validate the response and tier
    upload_response = upload_file(size_mb = 1000 , filename = "abcd.txt")
    assert upload_response.status_code == status.HTTP_201_CREATED
    assert upload_response.json()['tier'] == 'HOT'

    # Get the file_id and update last accessed to 31 days ago
    file_id = upload_response.json()['file_id']
    update_last_accessed(file_id,31)
    
    # Trigger auto-tiering and validate the tier movement to WARM
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 1
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'WARM'

    # Update last accessed to 91 days ago and trigger auto-tiering
    update_last_accessed(file_id,91)
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 1

    # Validate the tier movement to COLD
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'COLD'

    # Delete the file
    delete_response = delete_file(file_id)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT


def test_movement_from_HOT_to_COLD(upload_file,update_last_accessed,auto_tiering,get_metadata,delete_file):
    """
    This test covers:
    - Movement of files from HOT to COLD tier after 90 days of inactivity.
    """
    # Create and Upload a file and validate the response and tier
    upload_response = upload_file(size_mb = 1000 , filename = "abcd.txt")
    assert upload_response.status_code == status.HTTP_201_CREATED
    assert upload_response.json()['tier'] == 'HOT'

    # Get the file_id and update last accessed to 91 days ago for movement to COLD
    file_id = upload_response.json()['file_id']
    update_last_accessed(file_id,91)

    # Perform auto-tiering twice to ensure movement from HOT -> WARM -> COLD
    auto_tiering()
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 1

    # Validate the tier movement to COLD
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'COLD'

    # Delete the file
    delete_response = delete_file(file_id)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.skip(reason="Reverse tiering movement is not present")
def test_movement_from_COLD_to_WARM(upload_file,update_last_accessed,auto_tiering,get_metadata,download_file):
    """
    This test covers:
    - Movement of files from COLD to WARM tier after download operation.
    """
    # Create and Upload a file and validate the response and tier
    upload_response = upload_file(size_mb = 1000 , filename = "abcd.txt")
    assert upload_response.status_code == status.HTTP_201_CREATED
    assert upload_response.json()['tier'] == 'HOT'

    # Get the file_id and update last accessed to 91 days ago for movement to COLD
    file_id = upload_response.json()['file_id']
    update_last_accessed(file_id,91)

    # Perform auto-tiering twice to ensure movement from HOT -> WARM -> COLD
    auto_tiering()
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] >= 1

    # Validate the tier movement to COLD
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'COLD'

    # Download the file to update last accessed
    download_file(file_id)

    # Trigger auto-tiering and validate the tier movement to WARM
    auto_tiering()
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'WARM'


def test_no_tier_movement_when_below_transition_threshold(upload_file,update_last_accessed,auto_tiering,get_metadata,delete_file):
    """
    This test covers:
    - Ensuring that files do not move tiers if they have not crossed the inactivity thresholds.
    """
    # Create and Upload a file and validate the response and tier
    upload_response = upload_file(size_mb = 1000 , filename = "abcd.txt")
    assert upload_response.status_code == status.HTTP_201_CREATED
    assert upload_response.json()['tier'] == 'HOT'

    # Get the file_id and update last accessed to 29 days ago, which is below the threshold for movement to WARM
    file_id = upload_response.json()['file_id']
    update_last_accessed(file_id,29)

    # Perform auto-tiering and validate that there is no movement from HOT to WARM
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 0
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'HOT'

    # Update last accessed to 89 days ago, which is below the threshold for movement to COLD
    update_last_accessed(file_id,80)
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 1

    # Validate the movement from HOT to WARM
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'WARM'

    # Update last accessed to 89 days ago, which is below the threshold for movement to COLD
    update_last_accessed(file_id,89)
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 0

    # Validate that there is no movement from WARM
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'WARM'

    # Delete the file
    delete_response = delete_file(file_id)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

def test_tier_movement_of_priority_files(upload_file,update_last_accessed,auto_tiering,get_metadata,delete_file):
    """
    This test covers:
    - Ensuring that files with priority indicators in their names do not move tiers, 
      until they cross the maximum inactivity threshold.
    """
    # Create and Upload a PRIORITY file.
    upload_response = upload_file(size_mb = 1000 , filename = "abc_PRIORITY_")
    assert upload_response.status_code == status.HTTP_201_CREATED
    assert upload_response.json()['tier'] == 'HOT'

    # Get the file_id and update last accessed to 31 days ago, which is allocated to WARM tier.
    file_id = upload_response.json()['file_id']
    update_last_accessed(file_id,31)

    # Perform auto-tiering and validate the movement.
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 0
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'HOT'

    # Update last accessed to 91 days ago, which is allocated to COLD tier.
    update_last_accessed(file_id,91)
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 0
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'HOT'

    # Update last accessed to 181 days ago, which is above the threshold for movement to COLD.
    update_last_accessed(file_id,181)
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 0

    # Validate tiering, it should be HOT
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'HOT'

    # Delete the file
    delete_response = delete_file(file_id)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

def test_tier_movement_of_legal_files(upload_file,update_last_accessed,auto_tiering,get_metadata,delete_file):
    """
    This test covers:
    - Ensuring that files with legal indicators in their names do not move tiers,
      until they cross their designated thresholds.
    """
    # Create and Upload a LEGAL file.
    upload_response = upload_file(size_mb = 1000 , filename = "LEGAL_abcd")
    assert upload_response.status_code == status.HTTP_201_CREATED
    assert upload_response.json()['tier'] == 'HOT'

    # Update last accessed to 31 days ago, which is allocated to WARM tier.
    file_id = upload_response.json()['file_id']
    update_last_accessed(file_id,32)

    # Trigger auto-tiering and validate movement to WARM
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 1
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'WARM'

    # Update last accessed to 175 days ago, which is allocated to COLD tier,
    # but since it's a LEGAL file, it should not move to COLD until it crosses 180 days.
    update_last_accessed(file_id,175)
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 0
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'WARM'

    # EDGE CASE : Update last accessed to 180 days ago, which is the threshold for movement to COLD.
    # It must move to COLD tier on 180th day as per the business rule for LEGAL files.
    update_last_accessed(file_id,180)
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 1
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'COLD'

    # Update last accessed to 181 days ago, 
    # which is above the threshold for movement to COLD.
    update_last_accessed(file_id,181)
    tiering_response = auto_tiering()
    assert tiering_response.status_code == 200
    assert tiering_response.json()['files_moved'] == 0

    # Validate tiering, it should be COLD
    metadata = get_metadata(file_id).json()
    assert metadata['tier'] == 'COLD'

    # Delete the file
    delete_response = delete_file(file_id)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT




   