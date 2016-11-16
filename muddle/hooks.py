"""
Default plugin.

Each hook in this plugin will receive an instance of world.World as it's first argument.

If you wish this plugin to be loaded onto every new world, set global_plugin = True.
"""

global_plugin = False


def line_received(world, line):
    """
    The provided line was received by the provided world.

    line - An instance of line.Line.
    """
    pass


def pre_write(world, line):
    """
    The provided world is about to write the provided line to it's output.

    The line may have been modified by triggers or even plugins.

    line - An instance of line.Line.
    """
    pass

def command_entered(world, line):
    """
    A command was entered by the user in the provided world.
    
    This hook fires just after the user presses enter, so before any aliases have been invoked.

    line - An instance of line.Line.
    """
    pass


def pre_send(world, line):
    """
    The command identified by line is about to be sent to the connection of the provided world.
    
    The command may have been modified by one or more aliases.
    """
    pass


def plugin_loaded(world):
    """This plugin has been loaded to the provided world."""
    pass


def plugin_removed(world):
    """This plugin has been removed from the provided world."""
    pass
