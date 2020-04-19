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
                "POST0": {"results": [{"body": {"id": 1}}, {"body": {"id": 2}},]}
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


# TODO: error testing
