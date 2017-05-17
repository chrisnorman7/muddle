"""MUDdle client protocol."""

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ClientFactory
from .line import Line


class Protocol(LineReceiver):
    """Client protocol."""

    def __init__(self, world):
        """Initialise with a frame."""
        self.world = world
        world.protocol = self

    def log(self, message, level='info', *args, **kwargs):
        """Log a message."""
        logger = self.world.logger
        if hasattr(logger, level):
            getattr(logger, level)(message, *args, **kwargs)
        else:
            logger.critical(
                'Could not log message %r with args %r and kwargs %r because '
                'there is no such level %r.',
                message,
                args,
                kwargs,
                level
            )

    def connectionMade(self):
        """Connected."""
        self.log('Connected.')

    def lineReceived(self, line):
        """A line was received from the server."""
        line = Line(line)
        self.world.handle_plugins('line_received', line)
        for trigger in self.world.triggers:
            m = trigger.match(line)
            if m:
                if m is True:
                    args = []
                    kwargs = []
                else:
                    args = m.groups()
                    kwargs = m.groupdict()
                trigger.run(line, *args, **kwargs)
        self.world.handle_plugins('pre_write', line)
        if not line.gagged():
            self.world.frame.write(line.get_text())

    def connectionLost(self, reason):
        """The connection was lost."""
        self.log(reason.getErrorMessage())


class Factory(ClientFactory):
    """The factory to ship out new protocols."""
    def __init__(self, world):
        """Initialise with a frame."""
        self.world = world

    def log(self, message, *args, **kwargs):
        """Log a message formatted with ars and kwargs."""
        self.world.frame.write(
            '[Connection Factory]: ' + message.format(
                *args,
                **kwargs))

    def buildProtocol(self, addr):
        """Connection was made."""
        self.log('Connected to {}:{}.', addr.host, addr.port)
        return Protocol(self.world)

    def clientConnectionFailed(self, connector, reason):
        """Connecting to connector failed because of reason."""
        self.log(
            'Failed to connect to {}:{}: {}',
            connector.host,
            connector.port,
            reason.getErrorMessage())
