# Results

## Summary

* Run ID: cicada-2-run-42a97a75
* Successful Tests: 1
* Failed Tests: 0

## Tests
1. [send-messages](#send-messages)
* #### send-messages
    - Description: Send a message to service
    - Duration: 0 seconds
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
                  "runtime": 2
                }
                ```
    - Asserts:
        * FindMessage0
            - Number of Calls: 1
            - Failed Calls: 0
                ```json
                {
                  "actual": "{\u0027topic\u0027: \u0027outbound-files\u0027, \u0027key\u0027: \u0027fizz\u0027, \u0027value\u0027: \u0027buzz\u0027}",
                  "description": "passed",
                  "expected": "{\u0027key\u0027: \u0027fizz\u0027, \u0027value\u0027: \u0027buzz\u0027}",
                  "passed": true
                }
                ```
---
