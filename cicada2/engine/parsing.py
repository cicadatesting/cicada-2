import json
import base64
from os import getenv
from typing import Any

import jinja2
import yaml

from cicada2.shared.errors import ValidationError


def render_section(section: Any, state: dict, **kwargs: dict) -> Any:
    """
    Renders the 'template' section of a config block and replaces the key with the rendered yaml
    Section can also be a jinja2 string
    If the section is anything else, it is just returned without rendering

    Example:
        Before:
            foo: bar
            template: >
                fizz: buzz

        After:
            foo: bar
            fizz: buzz
            template: >
                fizz: buzz

    Args:
        section: Section to render (presumably has a template section)
        state: State to use in rendering section
        **kwargs: Other keys to provide to section during render

    Returns:
        Current section combined with rendered template data (will retain template string for future use)
    """
    try:
        if isinstance(section, dict) and "template" in section:
            template_string = section.get("template", "")
        elif isinstance(section, dict):
            return {
                key: render_section(section[key], state, **kwargs) for key in section
            }
        elif isinstance(section, str):
            template_string = section
        else:
            return section

        template = jinja2.Environment(
            loader=jinja2.BaseLoader, extensions=["jinja2.ext.do"]
        ).from_string(template_string)

        rendered_template_string = template.render(
            state=state, json=json, getenv=getenv, base64=base64, **kwargs
        )
    except (jinja2.TemplateError, jinja2.TemplateSyntaxError) as exc:
        raise ValidationError(f"Template section is invalid: {exc}")

    rendered_section_template = yaml.safe_load(rendered_template_string)

    if isinstance(section, dict) and rendered_section_template is None:
        rendered_section_template = {}

    if isinstance(section, dict) and isinstance(rendered_section_template, dict):
        return {**section, **rendered_section_template}
    else:
        return rendered_section_template
