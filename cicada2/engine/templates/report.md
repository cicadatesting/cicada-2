# Results

## Summary
{%- set successful = [] %}
{%- set failed = [] %}
{%- for test_name in state if test_name != 'globals' %}
    {%- set summary = state[test_name].get('summary') %}
    {%- if summary['error'] or summary['remaining_asserts']|length > 0 %}
        {%- do failed.append(test_name) %}
    {%- else %}
        {%- do successful.append(test_name) %}
    {%- endif %}
{%- endfor %}

* Run ID: {{ run_id }}
* Successful Tests: {{ successful|length }}
* Failed Tests: {{ failed|length }}

## Tests

{%- for test_name in state if test_name != 'globals' %}
{{ loop.index }}. [{{test_name}}](#{{test_name}})
{%- endfor %}

{%- for test_name in state if test_name != 'globals' %}
* #### {{ test_name }}
    {%- set summary = state[test_name].get('summary') %}
    - Duration: {{ summary['duration'] }} seconds
    - Completed Cycles: {{ summary['completed_cycles'] }}
    - Remaining Asserts: {{ summary['remaining_asserts']|length }}
    - Error: {{ summary['error'] }}
    {%- set actions = state[test_name].get('actions') %}
    {%- if actions is not none %}
    - Actions:
        {%- for action_name, action in actions.items() %}
        * {{ action_name }}
            {%- if action['results']|length > 0 %}
            - Number of Calls: {{ action['results']|length }}
            - Failed Calls: {{ action['results']|select("none")|list|length }}
            - Result
                ```json
                {{ action['results'][-1]|tojson(indent=2)|indent(16)|replace("&#34;", "\"") }}
                ```
            {%- elif action['results'] %}
            - Result
                ```json
                {{ action['results']|tojson(indent=2)|indent(16)|replace("&#34;", "\"") }}
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
        {%- for assert_name, asrt in asserts.items() %}
        * {{ assert_name }}
                {%- if asrt|length > 0 %}
            - Number of Calls: {{ asrt|length }}
            - Failed Calls: {{ asrt|map(attribute="passed")|select("false")|list|length }}
                ```json
                {{ asrt[-1]|tojson(indent=2)|indent(16)|replace("&#34;", "\"") }}
                ```
                {%- elif assert %}
                ```json
                {{ asrt|tojson(indent=2)|indent(16)|replace("&#34;", "\"") }}
                ```
            {%- endif %}
        {%- endfor %}
    {%- endif %}
---
{% endfor %}
