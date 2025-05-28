
import os
import threading
import platform
import time

from typing import Optional, Callable

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio, GdkPixbuf


def get_app_path():
    script_path = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.dirname(script_path)
    return app_path


def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            version = f.read()
            if "Microsoft" in version or "WSL" in version:
                return True
    except FileNotFoundError:
        pass
    if platform.uname().release.lower().find('microsoft') != -1:
        return True
    return False


if not is_wsl():
    try:
        gi.require_version('Notify', '0.7')
        from gi.repository import Notify
    except Exception:
        print("Optional: Install 'gir1.2-notify-0.7' to enable desktop notifications.")
    

class ClipBoard:
    def __init__(self):
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def copy(self, value):
        self.clipboard.set_text(value, -1)
        self.clipboard.store()



class Toolbar(Gtk.MenuBar):
    def __init__(self):
        super().__init__()

        self.commands = []


    def add_command(self, commands):
        if not isinstance(commands, list):
            raise ValueError("The 'commands' parameter must be a list of Gtk.MenuItem objects.")

        for command in commands:
            self.commands.append(command)
            self.append(command)
        self.show_all()



class Menu(Gtk.Menu):
    def __init__(self):
        super().__init__()
        self.items = []

    def add_commands(self, commands):
        if not isinstance(commands, list):
            raise ValueError("The 'commands' parameter must be a list of Gtk.MenuItem objects.")

        for command in commands:
            if not isinstance(command, Gtk.MenuItem):
                raise TypeError("All elements must be Gtk.MenuItem instances.")
            self.items.append(command)
            self.append(command)
        self.show_all()



class Command(Gtk.MenuItem):
    def __init__(
        self,
        title:str = None,
        action=None,
        sub_commands=None,
        tooltip:str = None,
        shortcut: str = None,
        accel_group: Gtk.AccelGroup = None,
        icon: str = None
    ):
        super().__init__()

        self._handler_id = None

        self._title = title
        self._action = action
        self._sub_commands = sub_commands
        self._tooltip = tooltip
        self._shortcut = shortcut
        self._accel_group = accel_group
        self._icon = icon

        self.app_path = get_app_path()
        self._build_item()

        self.set_label(self._title)

        if self._action:
            self.connect("activate", self._action)

        if self._sub_commands:
            submenu = Gtk.Menu()
            for sub_command in self._sub_commands:
                submenu.append(sub_command)
            submenu.show_all()
            self.set_submenu(submenu)
        
        if self._tooltip:
            self.set_tooltip_text(self._tooltip)

        if self._shortcut and self._accel_group:
            key, mod = Gtk.accelerator_parse(self._shortcut)
            self.add_accelerator(
                "activate", self._accel_group,
                key, mod, Gtk.AccelFlags.VISIBLE
            )
        
        
    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, new_action):
        if self._handler_id is not None:
            self.disconnect(self._handler_id)
            self._handler_id = None

        self._action = new_action
        if self._action:
            self._handler_id = self.connect("activate", self._action)

    
    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        self._build_item()

    
    def _build_item(self):
        child = self.get_child()
        if child:
            self.remove(child)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        if self._icon:
            try:
                icon_path = os.path.join(self.app_path, self._icon)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 16, 16)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                box.pack_start(image, False, False, 0)
            except Exception as e:
                print(f"Failed to load icon: {e}")

        label = Gtk.Label(label=self._title)
        label.set_xalign(0.0)
        box.pack_start(label, True, True, 0)
        if self._shortcut:
            friendly_shortcut = self.format_shortcut(self._shortcut)
            shortcut_label = Gtk.Label(label=friendly_shortcut)
            shortcut_label.set_xalign(1.0)
            box.pack_end(shortcut_label, False, False, 0)

        box.show_all()
        self.add(box)

    
    def format_shortcut(self, shortcut: str) -> str:
        replacements = {
            '<Control>': 'Ctrl+',
            '<Ctrl>': 'Ctrl+',
            '<Shift>': 'Shift+',
            '<Alt>': 'Alt+',
            '<Super>': 'Super+',
        }

        for gtk_key, readable in replacements.items():
            shortcut = shortcut.replace(gtk_key, readable)

        # Remove leftover angle brackets
        shortcut = shortcut.replace('<', '').replace('>', '')

        return shortcut



class CheckCommand(Gtk.CheckMenuItem):
    def __init__(
        self,
        title: str = None,
        on_toggled=None,
        active=False,
        tooltip:str = None
    ):
        super().__init__()

        self._on_toggled = None
        self._toggled_handler_id = None

        self._title = title
        self._tooltip = tooltip

        self.set_label(self._title)

        self.set_active(active)

        if on_toggled:
            self.connect("toggled", on_toggled)

        if self._tooltip:
            self.set_tooltip_text(self._tooltip)

    @property
    def active(self):
        return super().get_active()

    @active.setter
    def active(self, value: bool):
        super().set_active(value)

    @property
    def on_toggled(self):
        return self._on_toggled

    @on_toggled.setter
    def on_toggled(self, callback):
        if self._toggled_handler_id is not None:
            self.disconnect(self._toggled_handler_id)
            self._toggled_handler_id = None

        self._on_toggled = callback

        if callback:
            self._toggled_handler_id = self.connect("toggled", callback)



class StatusBar(Gtk.Statusbar):
    def __init__(self):
        super().__init__()
        self.context_id = self.get_context_id("statusbar")
    def add(self, value):
        self.push(self.context_id, value)


class StatusIconGtk:
    def __init__(
        self,
        icon: str,
        on_right_click: Optional[Callable] = None,
        on_left_click: Optional[Callable] = None,
        on_double_click: Optional[Callable] = None
    ):
        self.app_path = get_app_path()
        self.icon = os.path.join(self.app_path, icon)

        self.on_right_click = on_right_click
        self.on_left_click = on_left_click
        self.on_double_click = on_double_click

        self.last_click_time = 0
        self.double_click_threshold = 0.5

        self.status_icon = Gtk.StatusIcon()
        self.status_icon.set_from_file(self.icon)

        self.status_icon.connect("popup-menu", self.on_right_click_event)
        self.status_icon.connect("activate", self.on_left_click_event)

    def on_right_click_event(self, status_icon, button, time):
        if self.on_right_click:
            self.on_right_click()

    def on_left_click_event(self, status_icon):
        now = time.time()
        if (now - self.last_click_time) <= self.double_click_threshold:
            if self.on_double_click:
                self.on_double_click()
        else:
            if self.on_left_click:
                self.on_left_click()
        self.last_click_time = now

    def show(self):
        self.status_icon.set_visible(True)


class NotifyGtk():
    def __init__(
        self,
        title: str,
        message: str,
        duration: int,
        on_press: Optional[Callable] = None
    ):

        self.title = title
        self.message = message
        self.duration = duration
        self.on_press = on_press

        Notify.init("Btczwallet")
        self.notification = Notify.Notification.new(self.title, self.message)
        if self.on_press:
            self.notification.connect("closed", self.on_notification_click)

    def on_notification_click(self, notification):
        if self.on_press:
            self.on_press()

    def popup(self):
        self.notification.show()
        threading.Timer(self.duration, self.hide_notification).start()

    def hide_notification(self):
        self.notification.close()