"""Contains the Plugin class."""


class StopPropagation(StopIteration):
    """Stop hook propagation this round."""



class Plugin:
    """
    A worl plugin.

    When the plugin is initialised it will have it's world attribute set to
    the world it is attached to.

    Remember to set name and description on the class so they can be found by
    the plugin machinery.
    """

    name = 'Generic Plugin'
    description = 'This plugin needs a proper description.'

    def __init__(self, world):
        """Set self.world to world. That is the only initialisation which is
        performed."""
        self.world = world

    def stop(self, message=None):
        """Stop any future plugins from running."""
        if message:
            self.world.logger.info(
                'Plugin execution stopped by %r: %r',
                self, message)
        raise StopPropagation(message)

    def line_received(self, line):
        """
        The provided line was received by the world this plugin is attached to.

        line - An instance of line.Line.
        """
        pass

    def pre_write(self, line):
        """
    The world is about to write the provided line to it's output.

        The line may have been modified by triggers or even plugins.

        line - An instance of line.Line.
        """
        pass

    def command_entered(self, line):
        """
        A command was entered by the user in the attached world.

        This hook fires just after the user presses enter, so before any
        aliases have been invoked.

        line - An instance of line.Line.
        """
        pass

    def pre_send(self, line):
        """
        The command identified by line is about to be sent to the connection
        of the attached world.

        The command may have been modified by one or more aliases.
        """
        pass
