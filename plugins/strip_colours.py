"""Strip colours from output."""

import re
from .base import Plugin

escape = chr(27)
colour_re = re.compile(r'(%s\[[0-9]+m)' % escape)


class StripColoursPlugin(Plugin):
    name = 'Strip Colours'
    description = 'Strip colour tags from the output.'

    def line_received(world, line):
        text = line.get_text()
        if text:
            line.text = re.sub(colour_re, '', text)
