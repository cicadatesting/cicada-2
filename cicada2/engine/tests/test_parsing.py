# from cicada2.engine import state
# from tempfile import template
import pytest
from cicada2.shared.errors import ValidationError
from cicada2.engine import parsing


def test_render_section():
    template_string = """
        params:
            {% set ids = [] %}
            {% for member in state['add_members']['actions']['POST0']['results'] %}
            {% do ids.append(member['body']['id']) %}
            {% endfor %}
            query: "update members set name='jeff2' where id in ({{ ids|join(',') }})"
        """

    section = {"type": "SQLQuery", "template": template_string}

    state = {
        "add_members": {
            "actions": {
                "POST0": {
                    "results": [
                        {"body": {"id": 1}},
                        {"body": {"id": 2}},
                    ]
                }
            }
        }
    }

    rendered_section = parsing.render_section(section, state=state)

    assert rendered_section["type"] == "SQLQuery"
    assert rendered_section["params"] == {
        "query": "update members set name='jeff2' where id in (1,2)"
    }


def test_render_section_kwargs():
    template_string = """
        params:
            value: {{ state['foo'] + results['bar'] }}
        """

    state = {"foo": 2}
    results = {"bar": 4}
    section = {"template": template_string}

    rendered_section = parsing.render_section(section, state=state, results=results)
    assert rendered_section["params"]["value"] == 6


def test_render_section_string():
    template_string = "{{ state['foo'] }}"
    state = {"foo": 24}

    rendered_section = parsing.render_section(template_string, state=state)

    assert rendered_section == 24


def test_render_section_dict_no_template():
    section = {"foo": "{{ state['bar'] }}", "fizz": "{{ json.loads('true') }}"}
    state = {"bar": 24}

    rendered_section = parsing.render_section(section, state=state)

    assert rendered_section == {"foo": 24, "fizz": True}


def test_render_section_not_found():
    section = {"foo": "{{ bar }}"}

    rendered_section = parsing.render_section(section, state={})

    assert rendered_section == {"foo": None}


def test_render_section_state_not_found():
    section = {"foo": "{{ state['bar'] }}"}

    rendered_section = parsing.render_section(section, state={})

    assert rendered_section == {"foo": None}


def test_render_section_invalid_template():
    template_string = """
        {% for %}
        """

    state = {"foo": 2}
    section = {"template": template_string}

    with pytest.raises(ValidationError):
        parsing.render_section(section, state=state)
