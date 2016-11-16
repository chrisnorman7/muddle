"""Allow jinja2 parsing of commands."""

import application
from jinja2 import Environment

environment = Environment()

environment.globals['application'] = application


def pre_send(world, line):
    text = line.get_text()
    if text is not None:
        template = environment.from_string(text)
        line.substitute(template.render(world = world))
