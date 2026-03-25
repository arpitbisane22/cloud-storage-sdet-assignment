# Bug Report - File Storage Tiering System

This document lists identified defects in the File Storage Service based on test analysis.

---

## Bug 1: Files never moves in COLD -> WARM -> HOT direction.

**Severity:** High  
**Priority:** High  

### Description
If a file is in WARM or COLD tier, if it gets accessed then it should move to WARM or HOT tier respectively. This functionality is missing.

### Steps to Reproduce
1. Upload a file
2. Move it to COLD or WARM tier
3. Download the file
4. Check tiers from file metadata, it will remain in same tier.

### Expected Result
File should move to HOT or WARM tier

### Actual Result
File remains in same tier after accessing.

### Root Cause
From line 56 to 72 in storage_service.py,
Only next tier information is present, Tiering should be bi-directional

## Bug 2: LEGAL files remains in WARM tier instead of reaching their threshold.

**Severity:** High  
**Priority:** High  

### Description
If a LEGAL file is created, and it is 30 days old, it will be placed in WARM tier. But if it becomes 180 days old, it should move to COLD tier from WARM tier on 180th day. 

### Steps to Reproduce
1. Upload a LEGAL file
2. Keep it in WARM tier
3. Update the last access data to 180 days
4. Check tiering information,  it will be in WARM tier only.
5. On 181th day tiering changes to COLD

### Expected Result
File should move to COLD tier on 180th day

### Actual Result
File remains in WARM tier on 180th day

### Root Cause
line 180 in storage_service.py
if days_since_access <= 180:

### IMPROVEMENT
line 180 in storage_service.py
if days_since_access < 180: