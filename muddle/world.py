"""World class."""

import logging
import os
import os.path
from json import dump, load
from attr import attrs, attrib, Factory as AttrsFactory
from twisted.internet import reactor
import application
from .config import Config
from .triggers import Trigger, Alias
from .protocol import Factory
from plugins.base import StopPropagation

world_dir = os.path.join(application.config_dir, 'worlds')


@attrs
class World:
    """An instance of a world."""

    frame = attrib()
    config = attrib(default=AttrsFactory(Config))
    triggers = attrib(default=AttrsFactory(list))
    aliases = attrib(default=AttrsFactory(list))
    disabled = attrib(default=AttrsFactory(list))
    classes = attrib(default=AttrsFactory(list))
    protocol = attrib(default=AttrsFactory(lambda: None))

    def __attrs_post_init__(self):
        self.factory = Factory(self)
        self.logger = logging.getLogger('[World]')
        self.log_handler = logging.StreamHandler(self.frame)
        self.logger.addHandler(self.log_handler)
        self._plugins = set()
        self.plugins = set()
        for cls in application.global_plugins:
            self.load_plugin(cls)

    def save(self):
        """Save this world."""
        if not self.name:
            raise RuntimeError('Cannot save a world with no name.')
        d = {}
        d['config'] = self.config.json()
        d['plugins'] = list(self._plugins)
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
                self.name + '.world'
            ),
            'w'
        ) as f:
            dump(d, f, indent=4)

    def load(self, filename, reset=True):
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
        plugins = {cls.name: cls for cls in application.plugins}
        for name in data.get('plugins', []):
            if name in plugins:
                self.load_plugin(plugins[name])
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

    def load_plugin(self, cls):
        """Load the specified plugin onto this world."""
        name = cls.name
        self.logger.info('Loading plugin %s.', name)
        self._plugins.add(name)
        plugin = cls(self)
        self.plugins.add(plugin)

    def unload_plugin(self, plugin):
        """Unload the specified plugin from this world."""
        for p in self.plugins:
            if p is plugin or isinstance(p, plugin):
                name = p.name
                self.plugins.remove(p)
                self.logger.info('Removing plugin %s.', name)
                if name in self._plugins:
                    self._plugins.remove(name)
                break

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
        """Add thing to the appropriate attribute of self. Just does
        self.enable for the time being."""
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
            self.disabled
        ]:
            attr.clear()

    def update(self):
        """Update triggers and aliases, taking into account
        self.check_classes."""
        things = self.aliases + self.triggers + self.disabled
        self.clear_things()
        for thing in things:
            self.enable(thing)

    def send(self, line):
        """Send a line to the MUD."""
        reactor.callFromThread(self.protocol.sendLine, line.encode())

    def handle_plugins(self, attr, *args, **kwargs):
        """Pass args and kwargs to every plugin on this world with an
        attribute named attr."""
        for plugin in self.plugins:
            try:
                getattr(plugin, attr)(*args, **kwargs)
            except StopPropagation:
                break
            except Exception as e:
                self.logger.warning(
                    'Calling %s(%r, %r) on plugin %s caused a traceback:',
                    attr,
                    args,
                    kwargs,
                    plugin.name
                )
                self.logger.exception(e)

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
