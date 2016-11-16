"""Adds a countlag command which times lag (assuming the server supports the echo command)."""

from time import time

def plugin_loaded(world):
    world.started = None

def command_entered(world, line):
    if line.text == 'lagcounter':
        world.started = time()
        line.text = 'echo lag.test'


def line_received(world, line):
    if world.started is not None:
        if line.text == 'lag.test':
            line.text = 'Lag: %.3f seconds.' % (time() - world.started)
        world.started = None
