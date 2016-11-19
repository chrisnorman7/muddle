"""This module speaks any ungagged incoming lines."""

from .base import Plugin
from muddle.accessibility import system


class SpeakLinePlugin(Plugin):
    name = 'Speak Lines'
    description = 'Automatically speak lines before they are printed. Can be avoided by setting a dont_speak attribute.'

    def pre_write(self, line):
        text = line.get_text()
        if text is not None and not getattr(line, 'dont_speak', False):  # Ignore gagged lines.
            text = text.strip()
            if text:
                system.speak(text)
