# Results

## Summary

* Run ID: cicada-2-run-54ba4b33
* Successful Tests: 2
* Failed Tests: 0

## Tests
1. [add_members](#add_members)
2. [update_names](#update_names)
* #### add_members
    - Description: add 100 new members
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Actions:
        * POST0
            - Number of Calls: 100
            - Failed Calls: 0
            - Result
                ```json
                {
                  "body": {
                    "id": 100,
                    "name": "jeff"
                  },
                  "headers": {
                    "Content-Length": "35",
                    "Content-Type": "application/json",
                    "Date": "Tue, 15 Sep 2020 03:11:53 GMT",
                    "Server": "Werkzeug/1.0.1 Python/3.8.3"
                  },
                  "runtime": 3.193,
                  "status_code": 200,
                  "text": "{\n  \"id\": 100, \n  \"name\": \"jeff\"\n}\n"
                }
                ```
---

* #### update_names
    - Description: update names of new members
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
    - Error: None
    - Actions:
        * SQLQuery1
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "rows": []
                }
                ```
            - Outputs
                * index
                    ```json
                    1
                    ```
        * SQLQuery0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "rows": []
                }
                ```
    - Asserts:
        * EqualsRows0
            - Number of Calls: 1
            - Failed Calls: 0
                ```json
                {
                  "actual": "[{\u0027cnt\u0027: 100}]",
                  "description": "passed",
                  "expected": "[{\u0027cnt\u0027: 100}]",
                  "passed": true
                }
                ```
---
