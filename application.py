"""App-specific storage."""

import logging
import os
import os.path
import wx
from inspect import isclass
from importlib import import_module, reload
from time import time
from plugins.base import Plugin

logger = logging.getLogger(__name__)

name = 'MUDdle'
__version__ = '0.0.1'

app = wx.App()
app.SetAppName(name)
config_dir = wx.StandardPaths.Get().GetUserDataDir()

windows = []

plugins_dir = 'plugins'
plugin_modules = {}  # All the loaded plugin modules.
plugins = set()
global_plugins = set()


def reload_plugins():
    """Reload all available plugins."""
    started = time()
    for thing in [plugins, global_plugins]:
        thing.clear()
    for window in windows:
        window.world.plugins.clear()
    for filename in os.listdir(plugins_dir):
        if filename == 'base.py':
            continue  # Don't reload the base.py file.
        name, ext = os.path.splitext(filename)
        if ext == '.py':
            module_name = '{}.{}'.format(plugins_dir, name)
            if module_name in plugin_modules:
                action = 'Reload'
                func = reload
                arg = plugin_modules[module_name]
                del plugin_modules[module_name]
            else:
                action = 'Load'
                func = import_module
                arg = module_name
            try:
                logger.info('%sing module %s.', action, module_name)
                module = func(arg)
                logger.debug('%s(%r) = %r.', func.__name__, arg, module)
                plugin_modules[module_name] = module
            except Exception as e:
                logger.warning('Failed to %s module %s:', action, module_name)
                logger.exception(e)
                module = None
            if module is not None:  # Don't act on non-imported modules.
                logger.info('Searching for plugins.')
                for x in dir(module):
                    cls = getattr(module, x)
                    logger.debug('%s = %r.', x, cls)
                    if isclass(cls) \
                        and issubclass(cls, Plugin)\
                            and cls is not Plugin:
                        plugins.add(cls)
                        logger.info('Found plugin %s.', cls.name)
                    else:
                        logger.info(
                            'Ignoring attribute %s (%r, %r, %r).',
                            x,
                            isclass(cls),
                            issubclass(cls, Plugin) if isclass(cls) else 'N/A',
                            cls is not Plugin)
        else:
            logger.info('Ignoring file %s.', filename)
    logger.info(
        'Available plugins: %d (%.2f seconds).',
        len(plugins), time() - started)
