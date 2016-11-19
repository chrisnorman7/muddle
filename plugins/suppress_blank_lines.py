"""Suppress blank likes from appearing in the output."""

from .base import Plugin


class SuppressBlankLinesPlugin(Plugin):
    name = 'Suppress Blank Lines'
    description = 'Suppress blank lines from ever being processed.'

    def pre_write(self, line):
        text = line.get_text() or ''
        if not text.strip():
            line.gag()
            self.stop()
