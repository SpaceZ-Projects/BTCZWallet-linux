
from toga import App
from ..framework import StatusIconGtk, Gtk


class Notify(StatusIconGtk):
    def __init__(self, app:App):
        super().__init__(
            icon = "images/BitcoinZ-32.png",
            on_right_click=self.notify_on_click
        )

        self.app = app

    def notify_on_click(self, button, time):
        menu = Gtk.Menu()

        exit_cmd = Gtk.MenuItem(label="Exit")
        exit_cmd.connect("activate", self.exit_app)

        menu.append(exit_cmd)
        menu.show_all()

        menu.popup(None, None, None, None, button, time)


    def exit_app(self, action):
        self.app.exit()