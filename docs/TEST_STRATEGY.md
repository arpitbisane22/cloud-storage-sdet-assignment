# Test Strategy for File Storage & Tiering System

## 1. Overview
This document defines the testing strategy for the File Storage Service, which supports:
- File upload, download, and deletion
- Tier-based storage (HOT, WARM, COLD)
- Auto-tiering based on last accessed time
- File statistics tracking


The goal is to ensure tiering, correctness, reliability, and performance of the system under different scenarios.

---

## 2. Scope

### In Scope
- File Upload Operations
- File Download Operations
- File Deletion Operations
- Tiering Logic (HOT -> WARM -> COLD)
- Special file rules (LEGAL, PRIORITY)
- File Statistics (count, size, tier distribution)
- Concurrency and bulk operations

---

## 3. Test Modules Coverage

### 3.1 Upload Testing
Covered in: test_file_upload_operations.py 

- Upload with valid sizes and filenames
- Upload with invalid sizes (0, <1MB, >10GB)
- Upload with special filenames (LEGAL, PRIORITY)
- Edge cases:
  - Special characters
  - Empty names
  - Long filenames

---

### 3.2 Download Testing
Covered in: test_file_download_operations.py 

- Download valid file
- Download invalid/non-existent file
- Download after deletion
- Validate:
  - Content
  - Filename
  - Content-type
- Verify last_accessed update after download

---

### 3.3 Delete Testing
Covered in: test_file_delete_operations.py 

- Delete existing file
- Delete invalid/non-existent file
- Validate:
  - Metadata removal (404 after delete)

---

### 3.4 Tiering Logic Testing
Covered in: test_file_tiering_operations.py 

- HOT -> WARM (after 30 days)
- WARM -> COLD (after 90 days)
- HOT -> COLD transition ( HOT -> WARM -> COLD )
- No movement below thresholds
- Special rules:
  - PRIORITY files stay HOT
  - LEGAL files delayed movement in WARM Tier
- Edge cases:
  - Boundary values (29, 30, 89, 90, 180 days)

---

### 3.5 Fault Injection & Edge Cases
Covered in: test_fault_injection_and_edge.py 

- Files with multiple rules (LEGAL + PRIORITY)
- Tier validation across multiple files
- Upload with unusual filenames
    - Files with special characters
    - Files with " " name.
    - Files with very long name.

---

### 3.6 Stats Validation
Covered in: test_file_stats.py 

- Total file count validation
- Tier-wise count validation
- Stats after:
  - Upload
  - Delete
  - Tiering
- Response structure validation

---

### 3.7 Concurrency & Load Testing
Covered in: test_concurrent_operations.py

- Bulk operations (500 uploads/downloads/deletes)
- Concurrent uploads using ThreadPoolExecutor
- Concurrent downloads
- Concurrent deletes
- Concurrent tiering
- Data consistency validation under load

---

## 4. Testing Types

- Functional Testing
- Negative Testing
- Boundary Testing
- Edge Case Testing
- Concurrency Testing
- Data Consistency Testing
- API Testing

---

## 5. Test Approach

- Use pytest for test execution
- Use fixtures for reusable API operations (upload, delete, download)
- Use parametrization for multiple inputs
- Use ThreadPoolExecutor for concurrency testing
- Validate both:
  - API response
  - Backend metadata consistency

---

## 6. Test Data Strategy

- Dynamic file generation (size-based)
- Unique filenames using patterns
- Special test data:
  - LEGAL, PRIORITY indicators
  - Invalid sizes
  - Boundary values
  - Large-scale datasets (100–500 files)

---

## 7. Performance & Load Strategy

- Bulk upload testing (up to 500 files)
- Concurrent operations (100 threads)
- Tiering under load
- Stats validation under heavy operations

---

## 8. Advanced Considerations

- Validation of special rules (LEGAL + PRIORITY precedence)
- Data consistency after concurrent operations
- Tiering correctness across repeated executions


## Results
- 1 failed, 46 passed, 1 skipped, 1710 warnings in 466.89s (0:07:46)
- Total Testcases Executed: 48
- Passed: 46
- Failed: 1 (Bug number : 2)
- Skipped: 1 (Bug number : 1)
- Bugs found and documented in `BUGS_AND_IMPROVEMENTS.md`