# Results

## Summary
{%- set successful = [] %}
{%- set failed = [] %}
{%- for test_name in state %}
    {%- set summary = state[test_name].get('summary') %}
    {%- if summary['error'] or summary['remaining_asserts']|length > 0 %}
        {%- do failed.append(test_name) %}
    {%- else %}
        {%- do successful.append(test_name) %}
    {%- endif %}
{%- endfor %}

* Successful Tests: {{ successful|length }}
* Failed Tests: {{ failed|length }}

## Tests

{%- for test_name in state %}
* #### {{ test_name }}
    {%- set summary = state[test_name].get('summary') %}
    - Completed Cycles: {{ summary['completed_cycles'] }}
    - Remaining Asserts: {{ summary['remaining_asserts']|length }}
    - Error: {{ summary['error'] }}
    {%- set actions = state[test_name].get('actions') %}
    {%- if actions is not none %}
    - Actions:
        {%- for action_name, action in actions.items() %}
        * {{ action_name }}
            {%- if action['results']|length > 0 %}
            - Result
                ```json
                {{ action['results'][-1]|tojson(indent=2)|indent(16)|replace("&#34;", "\"") }}
                ```
            {%- endif %}
            {%- if action['outputs']|length > 0 %}
            - Outputs
                {%- for output_name, output in action['outputs'].items() %}
                * {{ output_name }}
                    ```json
                    {{ output|tojson }}
                    ```
                {%- endfor %}
            {%- endif %}
        {%- endfor %}
    {%- endif %}
    {%- set asserts = state[test_name].get('asserts') %}
    {%- if asserts is not none %}
    - Asserts:
        {%- for assert_name, assert in asserts.items() %}
        * {{ assert_name }}
            {%- if assert|length > 0 %}
            ```json
            {{ assert[-1]|tojson(indent=2)|indent(12)|replace("&#34;", "\"") }}
            ```
            {%- endif %}
        {%- endfor %}
    {%- endif %}
---
{% endfor %}
