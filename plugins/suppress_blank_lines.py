"""Suppress blank likes from appearing in the output."""


def pre_write(world, line):
    if not line.get_text().strip():
        line.gag()
