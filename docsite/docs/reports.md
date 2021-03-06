---
id: reports
title: Reports
sidebar_label: Reports
---

Once all the tests are finished, a Markdown test report is generated
using the final version of the state container, as well as JSON files
representing the state container after the completion of each test.

These files are available in the engine at `/reports`.

Example report generated by a test run:

https://github.com/herzo175/cicada-2/tree/master/example_services/rest_api/reports/report.md

In addition, the Cicada engine will return an exit code `0` if all tests pass
and complete successfully, or `1` otherwise. This can be overridden with the
[ERROR_CODE_OVERRIDE](config.md#error_code_override) setting.

Report verification can also be performed by running a
[verification](verification.md) container.
