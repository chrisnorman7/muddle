"""World class."""

import logging
import os
import os.path
from json import dump, load
import application
from .config import Config
from .triggers import Trigger, Alias
from .protocol import Factory
from twisted.internet import reactor

world_dir = os.path.join(application.config_dir, 'worlds')


class World:
    """An instance of a world."""
    def __init__(self, frame):
        """Initialise the world with a frame."""
        self.frame = frame
        self.config = Config()
        self.triggers = []
        self.aliases = []
        self.disabled = []
        self.classes = []
        self.factory = Factory(self)
        self.protocol = None
        self.logger = logging.getLogger('[World]')
        self.log_handler = logging.StreamHandler(self.frame)
        self.logger.addHandler(self.log_handler)
        self.plugins = {}
        for plugin in application.plugins.values():
            if plugin.global_plugin:
                self.load_plugin(plugin)

    def save(self):
        """Save this world."""
        if not self.name:
            raise RuntimeError('Cannot save a world with no name.')
        d = {}
        d['config'] = self.config.json()
        d['plugins'] = list(self.plugins)
        d['classes'] = self.classes
        d['triggers'] = []
        for t in self.triggers + self.disabled:
            if isinstance(t, Trigger):
                d['triggers'].append(t.dump())
        d['aliases'] = []
        for a in self.aliases + self.disabled:
            if isinstance(a, Alias):
                d['aliases'].append(a)
        if not os.path.isdir(world_dir):
            os.makedirs(world_dir)
        with open(
            os.path.join(
                world_dir,
                self.name + '.world'),
            'w') as f:
            dump(d, f, indent = 4)

    def load(self, filename, reset = True):
        """Load a world from filename."""
        with open(filename, 'r') as f:
            data = load(f)
        self.config.update(
            data.get('config', {}),
            ignore_missing_sections=False,
            ignore_missing_options=False)
        if reset:
            self.clear_things()
            self.classes.clear()
        for name in data.get('plugins', []):
            if name in application.plugins:
                plugin = application.plugins[name]
                self.load_plugin(plugin)
            else:
                self.logger.warning('No plugin found matching %s.', name)
        self.classes = data.get('classes', [])
        for t in data.get('triggers', []):
            self.add(Trigger(self, **t))
        for a in data.get('aliases', []):
            self.add(Alias(self, **a))
        if self.config.connection['hostname']:
            try:
                self.connect()
            except Exception as e:
                self.logger.critical('While connecting a traceback occurred:')
                self.logger.exception(e)
        else:
            self.logger.info(
                'Not connecting with no connection configured.')

    def load_plugin(self, plugin):
        """Load the specified plugin onto this world."""
        name = plugin.__name__
        self.logger.info('Loading plugin %s.', name)
        self.plugins[name] = plugin
        plugin.plugin_loaded(self)

    def unload_plugin(self, plugin):
        """Unload the specified plugin from this world."""
        name = plugin.__name__
        if name in self.plugins:
            del self.plugins[name]
            self.logger.info('Removing plugin %s.', name)
            plugin.plugin_removed(self)

    def connect(self):
        """Conect this world."""
        if not self.config.connection['hostname']:
            raise ValueError('No hostname to connect to.')
        reactor.connectTCP(
            self.config.connection['hostname'],
            self.config.connection['port'],
            self.factory)

    def disconnect(self):
        """Disconnect this world."""
        if self.protocol is None or not self.protocol.connected:
            raise ValueError('Not conected.')
        else:
            self.protocol.transport.loseConnection()

    def check_classes(self, classes):
        """Check the provided classes against the currently-loaded classes."""
        return not classes or [c for c in classes if c in self.classes]

    def add(self, thing):
        """Add thing to the appropriate attribute of self. Just does self.enable for the time being."""
        self.enable(thing)

    def enable(self, thing):
        """Enable or disable thing."""
        if self.check_classes(thing.classes):
            if isinstance(thing, Trigger):
                self.triggers.append(thing)
            elif isinstance(thing, Alias):
                self.aliases.append(thing)
            else:
                raise TypeError('No clue what to do with %r.' % thing)
        else:
            self.disabled.append(self)

    def enable_class(self, cls):
        """Enable a class."""
        self.classes.append(cls)
        self.update()

    def disable_class(self, cls):
        """Disable a class."""
        self.classes.disable(self, cls)
        self.update()

    def clear_things(self):
        """Clear triggers, aliases and disabled items."""
        for attr in [
            self.triggers,
            self.aliases,
            self.disabled]:
            attr.clear()

    def update(self):
        """Update triggers and aliases, taking into account self.check_classes."""
        things = self.aliases + self.triggers + self.disabled
        self.clear_things()
        for thing in things:
            self.enable(thing)

    def send(self, line):
        """Send a line to the MUD."""
        reactor.callFromThread(self.protocol.sendLine, line.encode())

    def handle_plugins(self, attr, *args, **kwargs):
        """Pass args and kwargs to every plugin on this world with an attribute named attr."""
        for plugin in self.plugins.values():
            getattr(plugin, attr, lambda *args, **kwargs: None)(self, *args, **kwargs)


    @property
    def name(self):
        """Get the name of the world."""
        return self.config.world['name']

    @name.setter
    def name(self, value):
        """Set the name of this world."""
        self.config.world['name'] = value
        self.log_handler.set_name(self.name)
        self.frame.SetTitle(self.name)

    @property
    def connected(self):
        """Return whether the world is connected."""
        return self.protocol is not None and self.protocol.connected
