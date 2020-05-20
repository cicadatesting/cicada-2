# Results

## Summary

* Run ID: cicada-2-run-d78ba94d
* Successful Tests: 4
* Failed Tests: 0

## Tests
1. [seed](#seed)
2. [send-messages](#send-messages)
3. [check-file-transform](#check-file-transform)
4. [teardown](#teardown)
* #### seed
    - Description: create test bucket
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Actions:
        * cb0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "runtime": 7
                }
                ```
        * put0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "runtime": 13
                }
                ```
        * put1
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "runtime": 8
                }
                ```
        * put2
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "runtime": 8
                }
                ```
---

* #### send-messages
    - Description: Send a message to service
    - Duration: 1 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Actions:
        * Send1
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "errors": [],
                  "messages_received": null,
                  "messages_sent": 1,
                  "runtime": 14
                }
                ```
        * Send0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "errors": [],
                  "messages_received": null,
                  "messages_sent": 1,
                  "runtime": 86
                }
                ```
        * Send2
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "errors": [],
                  "messages_received": null,
                  "messages_sent": 1,
                  "runtime": 16
                }
                ```
    - Asserts:
        * FindMessage2
            - Number of Calls: 1
            - Failed Calls: 0
                ```json
                {
                  "actual": "{\u0027topic\u0027: \u0027outbound-files\u0027, \u0027key\u0027: \u0027file_a\u0027, \u0027value\u0027: None}",
                  "description": "passed",
                  "expected": "{\u0027key\u0027: \u0027file_c\u0027}",
                  "passed": true
                }
                ```
        * FindMessage1
            - Number of Calls: 1
            - Failed Calls: 0
                ```json
                {
                  "actual": "{\u0027topic\u0027: \u0027outbound-files\u0027, \u0027key\u0027: \u0027file_a\u0027, \u0027value\u0027: None}",
                  "description": "passed",
                  "expected": "{\u0027key\u0027: \u0027file_b\u0027}",
                  "passed": true
                }
                ```
        * FindMessage0
            - Number of Calls: 1
            - Failed Calls: 0
                ```json
                {
                  "actual": "{\u0027topic\u0027: \u0027outbound-files\u0027, \u0027key\u0027: \u0027file_a\u0027, \u0027value\u0027: None}",
                  "description": "passed",
                  "expected": "{\u0027key\u0027: \u0027file_a\u0027}",
                  "passed": true
                }
                ```
---

* #### check-file-transform
    - Description: Check that file has been updated
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Asserts:
        * FilesEqual2
            - Number of Calls: 1
            - Failed Calls: 0
                ```json
                {
                  "actual": "s3://file-transform-service/file_c.json",
                  "description": "passed",
                  "expected": "/test_data/file_c.json",
                  "passed": true
                }
                ```
        * FilesEqual1
            - Number of Calls: 1
            - Failed Calls: 0
                ```json
                {
                  "actual": "s3://file-transform-service/file_b.json",
                  "description": "passed",
                  "expected": "/test_data/file_b.json",
                  "passed": true
                }
                ```
        * FilesEqual0
            - Number of Calls: 1
            - Failed Calls: 0
                ```json
                {
                  "actual": "s3://file-transform-service/file_a.json",
                  "description": "passed",
                  "expected": "/test_data/file_a.json",
                  "passed": true
                }
                ```
---

* #### teardown
    - Description: Delete temporary S3 bucket
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Actions:
        * rm0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "runtime": 68
                }
                ```
---
