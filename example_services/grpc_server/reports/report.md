# Results

## Summary

* Run ID: cicada-2-run-df169934
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
        * Unary2
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "error": null,
                  "metadata": {},
                  "response": {
                    "message": "Hello, jeff!"
                  }
                }
                ```
            - Asserts
                * Assert0
                    - Number of Calls: 1
                    - Failed Calls: 0
                        ```json
                        {
                          "actual": {
                            "error": null,
                            "metadata": {},
                            "response": {
                              "message": "Hello, jeff!"
                            }
                          },
                          "description": "passed",
                          "expected": {
                            "response": {
                              "message": "Hello, jeff!"
                            }
                          },
                          "passed": true
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
        * Unary1
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "error": null,
                  "metadata": {},
                  "response": {
                    "message": "Hello, jeff!"
                  }
                }
                ```
            - Asserts
                * Assert0
                    - Number of Calls: 1
                    - Failed Calls: 0
                        ```json
                        {
                          "actual": {
                            "error": null,
                            "metadata": {},
                            "response": {
                              "message": "Hello, jeff!"
                            }
                          },
                          "description": "passed",
                          "expected": {
                            "response": {
                              "message": "Hello, jeff!"
                            }
                          },
                          "passed": true
                        }
                        ```
---
