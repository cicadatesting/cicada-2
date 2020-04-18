import os

import jinja2


TEMPLATES_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# TODO: include more test/assert/action config information
# NOTE: possibly add support for displaying erred calls in non versioned results
# NOTE: May need to support displaying test duration in ms instead of seconds


def render_report(
        state: dict,
        templates_directory: str = TEMPLATES_DIRECTORY,
        template_file: str = 'report.md',
        **kwargs: dict
) -> str:
    """
    Performs jinja2 render on an entire report file with provided state dictionary

    Args:
        state: State dictionary to provide to report template
        templates_directory: Dir location of reports file template
        template_file: Name of report file template
        **kwargs: Other info to provide to template

    Returns:
        Rendered string of report
    """
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath=templates_directory),
        extensions=['jinja2.ext.do']
    ).get_template(template_file)

    return template.render(
        state=state,
        **kwargs
    )
