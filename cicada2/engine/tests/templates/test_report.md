# Results

## Summary

* Run ID: 12345
* Successful Tests: 0
* Failed Tests: 1

## Tests
1. [test-name](#test-name)
* #### test-name
    - Completed Cycles: 12
    - Remaining Asserts: 1
    - Error: 
    - Actions:
        * POST0
            - Number of Calls: 1
            - Failed Calls: 0
            - Result
                ```json
                {
                  "status_code": 200
                }
                ```
            - Outputs
                * index
                    ```json
                    [1, 2, 3]
                    ```
    - Asserts:
        * EqualsRows0
            - Number of Calls: 1
            - Failed Calls: 1
                ```json
                {
                  "actual": null,
                  "description": "Exception calling application: (psycopg2.errors.UndefinedTable) relation \"my_members\" does not exist\nLINE 1: select count(*) as cnt from my_members where name=\u0027jeff2\u0027\n                                    ^\n\n[SQL: select count(*) as cnt from my_members where name=\u0027jeff2\u0027]\n(Background on this error at: http://sqlalche.me/e/f405)",
                  "expected": null,
                  "passed": false
                }
                ```
---
