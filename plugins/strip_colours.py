"""Strip colours from output."""

import re
escape = chr(27)
colour_re = re.compile(r'(%s\[[0-9]+m)' % escape)


def line_received(world, line):
    line.text = re.sub(colour_re, '', line.text)
