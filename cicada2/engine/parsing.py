from typing import Dict, Any

import yaml
import jinja2


def render_section(section: dict, state: dict, **kwargs: Any) -> dict:
    template = jinja2.Environment(
        loader=jinja2.BaseLoader,
        extensions=['jinja2.ext.do']
    ).from_string(section.get('template', ''))

    try:
        rendered_template_string = template.render(state=state, **kwargs)
    except jinja2.TemplateError as exc:
        # TODO: custom error types
        raise ValueError(f"Template section is invalid: {exc}")

    rendered_section_template = yaml.safe_load(rendered_template_string)

    if rendered_section_template is None:
        rendered_section_template = {}

    return {**section, **rendered_section_template}
