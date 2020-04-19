import yaml
import jinja2


from cicada2.shared.errors import ValidationError


def render_section(section: dict, state: dict, **kwargs: dict) -> dict:
    """
    Renders the 'template' section of a config block and replaces the key with the rendered yaml

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
        template = jinja2.Environment(
            loader=jinja2.BaseLoader, extensions=["jinja2.ext.do"]
        ).from_string(section.get("template", ""))

        rendered_template_string = template.render(state=state, **kwargs)
    except (jinja2.TemplateError, jinja2.TemplateSyntaxError) as exc:
        raise ValidationError(f"Template section is invalid: {exc}")

    rendered_section_template = yaml.safe_load(rendered_template_string)

    if rendered_section_template is None:
        rendered_section_template = {}

    return {**section, **rendered_section_template}
