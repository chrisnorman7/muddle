"""This module speaks any ungagged incoming lines."""

from muddle.accessibility import system


def pre_write(world, line):
    text = line.get_text()
    if text is not None:  # Ignore gagged lines.
        text = text.strip()
        if text:
            system.speak(text)
