# Results

## Summary

* Run ID: cicada-2-run-415940e5
* Successful Tests: 1
* Failed Tests: 0

## Tests
1. [greeter-requests](#greeter-requests)
* #### greeter-requests
    - Description: Send requests to greeter service
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Actions:
        * BidirectionalStreaming0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "error": null,
                  "metadata": {
                    "checksum-bin": "SSBhZ3JlZQ==",
                    "retry": "false"
                  },
                  "response": [
                    {
                      "message": "Hello, alice!"
                    },
                    {
                      "message": "Hello, bob!"
                    }
                  ]
                }
                ```
        * Unary0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "error": {
                    "code": "StatusCode.UNIMPLEMENTED",
                    "details": "Method not implemented!"
                  },
                  "metadata": null,
                  "response": null
                }
                ```
    - Asserts:
        * ResponseAssert0
            - Number of Calls: 1
            - Failed Calls: 0
                ```json
                {
                  "actual": "{\"message\": \"Hello, jeff!\"}",
                  "description": "\"passed\"",
                  "expected": "{\"message\": \"Hello, jeff!\"}",
                  "passed": true
                }
                ```
---
