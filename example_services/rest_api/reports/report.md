# Results

## Summary

* Run ID: cicada-2-run-db2762ec
* Successful Tests: 2
* Failed Tests: 0

## Tests
1. [add_members](#add_members)
2. [update_ages](#update_ages)
* #### add_members
    - Description: add 100 new members
    - Duration: 1 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 0
    - Error: None
    - Actions:
        * POST0
            - Number of Calls: 100
            - Failed Calls: 0
            - Result
                ```json
                {
                  "body": {
                    "id": 200,
                    "name": "jeff"
                  },
                  "headers": {
                    "Content-Length": "35",
                    "Content-Type": "application/json",
                    "Date": "Mon, 27 Apr 2020 22:20:49 GMT",
                    "Server": "Werkzeug/1.0.1 Python/3.8.2"
                  },
                  "runtime": 6.533,
                  "status_code": 200,
                  "text": "{\n  \"id\": 200, \n  \"name\": \"jeff\"\n}\n"
                }
                ```
---

* #### update_ages
    - Description: update ages of new members
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 0
    - Error: None
    - Actions:
        * SQLQuery0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "rows": []
                }
                ```
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
