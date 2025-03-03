
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class ClipBoard:
    def __init__(self):
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def copy(self, value):
        self.clipboard.set_text(value, -1)
        self.clipboard.store()


class StatusBar(Gtk.Statusbar):
    def __init__(self):
        super().__init__()
        self.context_id = self.get_context_id("statusbar")
    def add(self, value):
        self.push(self.context_id, value)