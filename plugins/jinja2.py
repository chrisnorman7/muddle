"""Allow jinja2 parsing of commands."""

import application
from jinja2 import Environment
from .base import Plugin

environment = Environment()

environment.globals['application'] = application


class Jinja2Plugin(Plugin):
    name = 'Jinja2'
    description = 'Format commands with Jinja2.'

    def pre_send(self, line):
        text = line.get_text()
        if text is not None:
            template = environment.from_string(text)
            line.substitute(template.render(world=self.world))
