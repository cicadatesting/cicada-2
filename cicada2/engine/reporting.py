import os
import json

import jinja2


TEMPLATES_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# TODO: include more test/assert/action config information
# NOTE: possibly add support for displaying erred calls in non versioned results


def render_report(
        state,
        templates_directory=TEMPLATES_DIRECTORY,
        template_file='report.md',
        **kwargs
):
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath=templates_directory),
        extensions=['jinja2.ext.do']
    ).get_template(template_file)

    return template.render(
        state=state,
        json=json,
        **kwargs
    )
