"""Triggers and aliases."""

import re
from lupa import LuaRuntime

lua = LuaRuntime()


class Trigger:
    """A trigger."""
    def __init__(
        self,
        world,
        name=None,
        pattern=None,
        regexp=True,
        code='',
        literal=False,
        classes=[]):
        """Initialise the trigger."""
        self.world = world
        self.name = name
        self.regexp = regexp
        self.code = code
        self.literal = literal
        self.classes = classes
        self.update()

    def match(self, line):
        """"Match this trigger against the provided line."""
        if not line.gagged():
            if self.pattern is None:
                return False
            elif not self.regexp:
                return line.get_text() == self.pattern
            else:
                return self._pattern.match(line.get_text())

    def update(self):
        """Update this trigger."""
        if self.regexp:
            self._pattern = re.compile(self.pattern)
        else:
            self._pattern = None
        if self.literal:
            self._func = None
        else:
            self._func = lua.eval('function(trigger, line, args, kwargs)\n{}\nend'.format(self.code))

    def run(self, line, *args, **kwargs):
        """Run the code of this trigger with line, args and kwargs."""
        if self.literal:
            self.world.send(self.code.format(*args, **kwargs))
        else:
            self._func(self, line, args, kwargs)

    def dump(self):
        """Return self as a dictionary."""
        return {
            'name': self.name,
            'pattern': self.pattern,
            'regexp': self.regexp,
            'code': self.code,
            'literal': self.literal,
            'classes': self.classes}


class Alias(Trigger):
    """
    An alias.

    The pattern attribute is used as the calling line.
    Using the gag method on a line with the function stops the alias from reaching the MUD.
    """
    pass
