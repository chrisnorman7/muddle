"""App-specific storage."""

import logging

logger = logging.getLogger(__name__)

name = 'MUDdle'
__version__ = '0.0.1'

import wx

app = wx.App()
app.SetAppName(name)
config_dir = wx.StandardPaths.Get().GetUserDataDir()

windows = []

plugins_dir = 'plugins'
plugins = {}

import os
import os.path
from importlib import import_module, reload
from time import time
from muddle import hooks

def reload_plugins():
    """Reload all available plugins."""
    started = time()
    if not os.path.isdir(plugins_dir):
        os.makedirs(plugins_dir)
    for filename in os.listdir(plugins_dir):
        name, ext = os.path.splitext(filename)
        if ext == '.py':
            module_name = '{}.{}'.format(plugins_dir, name)
            try:
                if module_name in plugins:
                    logger.info('Reloading plugin %s.', module_name)
                    module = reload(plugins[module_name])
                else:
                    logger.info('Loading plugin %s.', module_name)
                    module = import_module(module_name)
                for x in dir(hooks):
                    if not x.startswith('_') and not x.endswith('_'):
                        hook = getattr(hooks, x)
                        if not hasattr(module, x):
                            logger.info('Patching missing %s.%s.', module_name, x)
                            setattr(module, x, hook)
                plugins[module_name] = module
            except Exception as e:
                logger.warning('Failed to load plugin %s:', module_name)
                logger.exception(e)
        else:
            logger.info('Ignoring file %s.', filename)
    logger.info('Available plugins: %d (%.2f seconds).', len(plugins), time() - started)
