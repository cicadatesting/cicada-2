# Results

## Summary

* Run ID: cicada-2-run-eab8413a
* Successful Tests: 2
* Failed Tests: 0

## Tests
1. [add_members](#add_members)
2. [update_names](#update_names)
* #### add_members
    - Description: add 100 new members
    - Filename: /tests/test.cicada.yaml
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
                    "Date": "Sun, 15 Nov 2020 02:31:21 GMT",
                    "Server": "Werkzeug/1.0.1 Python/3.8.3"
                  },
                  "runtime": 4.783,
                  "status_code": 200,
                  "text": "{\n  \"id\": 100, \n  \"name\": \"jeff\"\n}\n"
                }
                ```
---

* #### update_names
    - Description: update names of new members
    - Filename: /tests/test.cicada.yaml
    - Duration: 0 seconds
    - Completed Cycles: 1
    - Remaining Asserts: 
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
