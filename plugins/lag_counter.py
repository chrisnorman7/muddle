"""Adds a countlag command which times lag (assuming the server supports the echo command)."""

from time import time
from .base import Plugin

class LagCounterPlugin(Plugin):
    name = 'Lag Counter'
    description = 'Count lag with the lagcounter command (assuming the attached world has a "echo" command.'

    def __init__(self, world):
        super(LagCounterPlugin, self).__init__(world)
        self.started = None
        self.cmd = 'lagcounter'
        self.mud_cmd = 'echo'
        self.trigger = 'lag.test'

    def command_entered(self, line):
        if line.text == self.cmd:
            line.text = '{} {}'.format(self.mud_cmd, self.trigger)
            self.started = time()
            self.stop()

    def line_received(self, line):
        if self.started is not None:
            if line.text == self.trigger:
                line.text = 'Lag: %.3f seconds.' % (time() - self.started)
            self.started = None
            self.stop()
