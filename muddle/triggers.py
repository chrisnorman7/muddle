"""Triggers and aliases."""

import re
from attr import attrs, attrib, Factory
from lupa import LuaRuntime

lua = LuaRuntime()


@attrs
class Trigger:
    """A trigger."""

    world = attrib()
    name = attrib(default=Factory(lambda: None))
    pattern = attrib(default=Factory(lambda: None))
    regexp = attrib(default=Factory(lambda: True))
    code = attrib(default=Factory(str))
    literal = attrib(default=Factory(bool))
    classes = attrib(default=Factory(list))

    def __attrs_post_init__(self):
        """Finish initialising the trigger."""
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
            self._func = lua.eval(
                'function(trigger, line, args, kwargs)\n{}\nend'.format(
                    self.code
                )
            )

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
    Using the gag method on a line with the function stops the alias from
    reaching the MUD.
    """
    pass
