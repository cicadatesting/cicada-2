# Results

## Summary

* Run ID: cicada-2-run-838579a7
* Successful Tests: 4
* Failed Tests: 0

## Tests
1. [seed](#seed)
2. [send-messages](#send-messages)
3. [check-file-transform](#check-file-transform)
4. [teardown](#teardown)
* #### seed
    - Description: create test bucket
    - Filename: /tests/test.cicada.yaml
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Actions:
        * cb0
            - Number of Calls: 1
            - Failed Calls: 1
            - Result
                ```json
                null
                ```
        * put0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "runtime": 10
                }
                ```
        * put1
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "runtime": 4
                }
                ```
        * put2
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "runtime": 4
                }
                ```
---

* #### send-messages
    - Description: Send a message to service
    - Filename: /tests/test.cicada.yaml
    - Duration: 1 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Actions:
        * Send0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "errors": [],
                  "messages_received": null,
                  "messages_sent": 1,
                  "runtime": 55.686
                }
                ```
        * Send1
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "errors": [],
                  "messages_received": null,
                  "messages_sent": 1,
                  "runtime": 5.768
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
                  "runtime": 7.568
                }
                ```
    - Asserts:
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
---

* #### check-file-transform
    - Description: Check that file has been updated
    - Filename: /tests/test.cicada.yaml
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Asserts:
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
---

* #### teardown
    - Description: Delete temporary S3 bucket
    - Filename: /tests/test.cicada.yaml
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
                  "runtime": 23
                }
                ```
---
