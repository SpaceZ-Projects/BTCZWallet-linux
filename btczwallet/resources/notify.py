
from toga import App
from ..framework import StatusIconGtk, Gtk

from .client import Client


class Notify(StatusIconGtk):
    def __init__(self, app:App, home_page, mining_page):
        super().__init__(
            icon = "images/BitcoinZ-32.png",
            on_right_click=self.notify_on_click
        )

        self.app = app
        self.home_page = home_page
        self.mining_page = mining_page

        self.commands = Client(self.app)

    def notify_on_click(self, button, time):
        menu = Gtk.Menu()
        
        stop_exit_cmd = Gtk.MenuItem(label="Stop node")
        stop_exit_cmd.connect("activate", self.stop_node_exit)
        exit_cmd = Gtk.MenuItem(label="Exit")
        exit_cmd.connect("activate", self.exit_app)

        menu.append(stop_exit_cmd)
        menu.append(exit_cmd)
        menu.show_all()

        menu.popup(None, None, None, None, button, time)


    def exit_app(self, action):
        if self.mining_page.mining_status:
            return
        self.home_page.clear_cache()
        self.app.exit()


    async def stop_node(self, widget):
        await self.commands.stopNode()
        self.home_page.clear_cache()
        self.app.exit()


    def stop_node_exit(self, action):
        if self.mining_page.mining_status:
            return
        self.app.add_background_task(self.stop_node)