
import os
import threading
import platform

from typing import Optional, Callable

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


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
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify
    

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


class StatusIconGtk:
    def __init__(
        self,
        icon: str,
        on_right_click: Optional[Callable] = None
    ):
        
        self.app_path  = get_app_path()

        self.icon= os.path.join(self.app_path ,icon)
        if on_right_click:
            self.on_right_click = on_right_click


        self.status_icon = Gtk.StatusIcon()
        self.status_icon.set_from_file(self.icon)

        self.status_icon.connect("popup-menu", self.on_right_click_event)

    def on_right_click_event(self, status_icon, button, time):
        if self.on_right_click:
            self.on_right_click(button, time)

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
        self.app_path  = get_app_path()

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