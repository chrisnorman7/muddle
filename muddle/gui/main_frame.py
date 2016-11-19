"""Main frame."""

import logging
import wx
from simpleconf.dialogs.wx import SimpleConfWxDialog
import application
from ..line import Line
from ..world import World, world_dir
from twisted.internet import reactor

logger = logging.getLogger(__name__)


class MainFrame(wx.Frame):
    """A MUDdle world frame."""
    def __init__(self, filename=None):
        """Create a new world."""
        self.world = World(self)
        super(MainFrame, self).__init__(None, title=self.world.name or 'Untitled World')
        p = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        self.entry_label = wx.StaticText(p, label = '&Entry')
        self.entry = wx.TextCtrl(p, style = wx.TE_RICH | wx.TE_PROCESS_ENTER)
        self.entry.Bind(wx.EVT_TEXT_ENTER, self.do_send)
        s.AddMany(
            [
                (self.entry_label, 0, wx.GROW),
                (self.entry, 1, wx.GROW)])
        s1 = wx.BoxSizer(wx.VERTICAL)
        self.output_label = wx.StaticText(p, label = '&Output')
        self.output = wx.TextCtrl(p, style = wx.TE_MULTILINE | wx.TE_READONLY)
        s1.AddMany(
            [
                (self.output_label, 0, wx.GROW),
                (self.output, 1, wx.GROW)])
        s.Add(s1, 1, wx.GROW)
        p.SetSizerAndFit(s)
        application.windows.append(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.file_menu = wx.Menu()
        self.add_menu_item(self.file_menu, 'E&xit', lambda event: self.Close(True), id = wx.ID_EXIT)
        self.world_menu = wx.Menu()
        self.add_menu_item(self.world_menu, '&Save', lambda event: self.world.save(), id = wx.ID_SAVE)
        self.add_menu_item(self.world_menu, '&Load...', self.do_load, id = wx.ID_OPEN)
        self.add_menu_item(self.world_menu, '&Connect', self.do_connect)
        self.add_menu_item(self.world_menu, '&Disconnect', self.do_disconnect)
        self.plugins_menu = wx.Menu()
        self.add_menu_item(self.plugins_menu, 'Load &World Plugin...', self.load_local_plugin)
        self.add_menu_item(self.plugins_menu, 'Load &Global Plugin...', self.load_global_plugin)
        self.add_menu_item(self.plugins_menu, '&Reload', lambda event: application.reload_plugins())
        self.preferences_menu = wx.Menu()
        for section in self.world.config.section_order:
            self.add_menu_item(self.preferences_menu, '&%s' % section.title, lambda event, section = section: SimpleConfWxDialog(section, parent = self).Show(True))
        self.world_menu.AppendSubMenu(self.preferences_menu, '&Preferences')
        self.menubar = wx.MenuBar()
        self.menubar.Append(self.file_menu, '&File')
        self.menubar.Append(self.world_menu, '&World')
        self.menubar.Append(self.plugins_menu, '&Plugins')
        self.SetMenuBar(self.menubar)
        self.Show(True)
        self.Maximize()
        if filename is not None:
            self.world.load(filename)

    def on_close(self, event):
        """Window is about to close."""
        if self.world.connected:
            reactor.callFromThread(self.world.protocol.transport.loseConnection)
        event.Skip()

    def write(self, text):
        """Write some text to the output window."""
        def f(text):
            try:
                self.output.AppendText(text + '\n')
            except Exception as e:
                logger.exception(e)
        wx.CallAfter(f, text)

    def add_menu_item(self, menu, name, handler, description = '', id = None):
        """Add a new item to menu, binding in the process."""
        if id is None:
            id = wx.NewId()
        item = menu.Append(id, name, description)
        self.Bind(wx.EVT_MENU, handler, item)

    def do_error(self, message, title='Error', style=wx.ICON_EXCLAMATION):
        """Display an error."""
        wx.MessageBox(str(message), title, style=style)

    def do_load(self, event):
        """Load tis world."""
        dlg = wx.FileDialog(
            self,
            defaultDir=world_dir,
            wildcard='*.world',
            style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
        else:
            filename = None
        dlg.Destroy()
        if filename:
            try:
                self.world.load(filename)
            except Exception as e:
                self.do_error(e)

    def do_connect(self, event):
        """Connect the world."""
        def f():
            try:
                if self.world.connected:
                    raise RuntimeError('This world is already connected.')
                self.world.connect()
            except Exception as e:
                wx.CallAfter(self.do_error, e)
        reactor.callFromThread(f)

    def do_disconnect(self, event):
        """Disconnect the world."""
        def f():
            try:
                self.world.disconnect()
            except Exception as e:
                wx.CallAfter(self.do_error, e)
        reactor.callFromThread(f)

    def load_plugins(self, worlds):
        """Load a plugin to 1 or more worlds."""
        plugins = sorted(application.plugins, key = lambda plugin: plugin.name)
        dlg = wx.MultiChoiceDialog(
            self,
            'Select plugins to load',
            'Plugins',
            ['{}: {}'.format(cls.name, cls.description) for cls in plugins])
        if dlg.ShowModal() == wx.ID_OK:
            indexes = dlg.GetSelections()
        else:
            indexes = []
        dlg.Destroy()
        for index in indexes:
            cls = plugins[index]
            for world in worlds:
                world.load_plugin(cls)

    def load_local_plugin(self, event):
        """Load a plugin to the current world."""
        self.load_plugins([self.world])

    def load_global_plugin(self, event):
        """Load a plugin to every world."""
        return self.load_plugins([window.world for window in application.windows])

    def do_send(self, event):
        """Send a line to the MUD."""
        line = Line(self.entry.GetValue())
        try:
            self.world.handle_plugins('command_entered', line)
            if line.gagged():
                return # Go no further.
            for alias in self.world.aliases:
                m = alias.match(line)
                if m:
                    if m is True:
                        args = []
                        kwargs = {}
                    else:
                        args = m.groups()
                        kwargs = m.groupdict()
                    alias.run(line, *args, **kwargs)
            self.world.handle_plugins('pre_send', line)
            if not line.gagged() and self.world.connected:
                self.world.send(line.get_text())
                self.entry.Clear()
            else:
                raise RuntimeError('Not connected.')
        except Exception as e:
            self.do_error(e)
