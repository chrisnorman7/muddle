"""World configuration."""

from simpleconf import Section, Option, validators


class Config(Section):
    """World configuration."""
    class world(Section):
        """World configuration."""
        title = 'World'
        name = Option(
            '',
            title='World &name',
            validator=validators.RestrictedString(min=4))
        description = Option(
            '')
        autosave = Option(
            True, title='&Autosave on exit',
            validator=validators.Boolean)
        option_order = [name, description, autosave]

    class connection(Section):
        """Connection information."""
        title = 'Connection'
        hostname = Option(
            '',
            title='&Hostname')
        port = Option(
            7777,
            title='&Port',
            validator=validators.Integer(min=1, max=65535))
        option_order = [hostname, port]

    class entry(Section):
        """Entry configuration."""
        title = 'Entry'
        command_interval = Option(
            0.0,
            title='&How fast commands should be sent',
            validator=validators.Float(
                min=0.0))
        option_order = [command_interval]

    section_order = [
        world,
        connection,
        entry]
