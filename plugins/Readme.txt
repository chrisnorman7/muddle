Creating plugins

To create a plugin you must subclass the Plugin class, and override it's methods.

Here is an example of creating a plugin with no functionality:

from .base import Plugin  # Remember we are using Python 3.


class MyPlugin(Plugin):
    name = 'My Plugin'
    description = 'A featureless plugin.'

That is enough code to create a plugin.

Don't forget to save your plugin file with a .py extension and place it into the plugins directory.

For documentation on the methods which can be overridden, see the base.py file.

When the client starts (or plugins are reloaded), each file in the plugins directory is loaded as a module.

Each module is checked for subclasses of Plugin (which can be named anything).

When a plugin is loaded to a world, that class is instantiated with the world as the first argument. This way you can always be sure of which world is using your plugin.

Useful methods:
stop - Stop the hook from propagating.
Use this if you want to make the current plugin the last in the chain.

Useful Properties:
world - The world which this plugin is attached to.
