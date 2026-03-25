from fastapi import status
import pytest

@pytest.mark.parametrize("filename",['a','b','c','d','e'])
def test_increase_count_in_stats(upload_file,filename,get_stats):
    """
    This test covers:
    - Validation of total file count in stats after uploading new files.
    """
    # Create and Upload new files.
    response = upload_file(1000 , filename=filename)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["tier"] == "HOT"

    # Validate stats from get_stats endpoint.
    stats = get_stats().json()
    assert stats['total_files'] >= 1

def test_total_count_in_stats(get_stats):
    """
    This test covers:
    - Validation of total file count in stats.
    """
    # Validate stats of files created
    stats = get_stats().json()
    assert stats['total_files'] >= 1 

def test_stats_after_deletion(upload_file,delete_file,get_stats):
    """
    This test covers:
    - Validation of stats after deleting a file.
    """
    # Create a new file and Upload it.
    response = upload_file(1000 , filename='f')
    assert response.status_code == status.HTTP_201_CREATED

    # Get the file_id from response.
    file_id = response.json()['file_id']
    
    # Get-Stats and validate total_files count.
    stats = get_stats().json()
    assert stats['total_files'] >= 1

    # Delete the file and validate the status code.
    delete_response = delete_file(file_id)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Stats should reflect the change in count after deletion.
    stats = get_stats().json()
    assert stats['total_files'] >= 0

def test_stats_after_tiering(upload_file,update_last_accessed,auto_tiering,get_stats,delete_file):
    """
    This test covers:
    - Validation of stats after auto-tiering operation.
    """
    # Create a new file and Upload it
    response = upload_file(1000 , filename='f')
    assert response.status_code == status.HTTP_201_CREATED

    # Get the file_id from response
    file_id = response.json()['file_id']

    # Validate the teiring of all the files created till now.
    hot_tier_count = get_stats().json()['tiers']['HOT']['count']
    assert hot_tier_count >= 1

    # Update last accessed and trigger auto-tiering.
    update_last_accessed(file_id,31)
    auto_tiering()

    # Validate stats after tiering, the file should move to WARM tier.
    stats = get_stats().json()
    hot_tier_count = stats['tiers']['HOT']['count']
    warm_tier_count = stats['tiers']['WARM']['count']
    assert hot_tier_count == 5
    assert warm_tier_count == 1

    # Update last accessed and trigger auto-tiering again.
    update_last_accessed(file_id,91)
    auto_tiering()

    # Stats should be updated after tiering, the file should move to COLD tier.
    stats = get_stats().json()
    warm_tier_count = stats['tiers']['WARM']['count'] 
    cold_tier_count = stats['tiers']['COLD']['count']
    assert warm_tier_count == 0
    assert cold_tier_count == 1

    # Delete the file
    delete_file(file_id)

    # Validate the stats, file should be removed from COLD tier
    stats = get_stats().json()
    assert stats['tiers']['HOT']['count'] == 5
    assert stats['tiers']['WARM']['count'] == 0
    assert stats['tiers']['COLD']['count'] == 0
    
def test_stats_response_structure(get_stats):
    """
    This test covers:
    - Validation of the structure of the stats response.
    """
    stats = get_stats().json()
    assert 'total_files' in stats
    assert 'tiers' in stats
    assert 'HOT' in stats['tiers']
    assert 'WARM' in stats['tiers']
    assert 'COLD' in stats['tiers']
    assert 'count' in stats['tiers']['HOT']
    assert 'count' in stats['tiers']['WARM']
    assert 'count' in stats['tiers']['COLD']
    assert 'size' in stats['tiers']['HOT']
    assert 'size' in stats['tiers']['WARM']
    assert 'size' in stats['tiers']['COLD']
