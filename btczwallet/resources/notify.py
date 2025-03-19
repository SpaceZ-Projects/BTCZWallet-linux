
from toga import App, Window
from ..framework import StatusIconGtk, Gtk

from .client import Client


class Notify(StatusIconGtk):
    def __init__(self, app:App, main:Window, home_page, mining_page):
        super().__init__(
            icon = "images/BitcoinZ-32.png",
            on_right_click=self.notify_on_click
        )

        self.app = app
        self.main = main
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
        def on_result(widget, result):
            if result is True:
                self.home_page.clear_cache()
                self.app.exit()
        if self.mining_page.mining_status:
            return
        self.main.question_dialog(
            title="Exit app",
            message="Are you sure you want to exit the application ?",
            on_result=on_result
        )


    async def stop_node(self, widget):
        await self.commands.stopNode()
        self.home_page.clear_cache()
        self.app.exit()


    def stop_node_exit(self, action):
        def on_result(widget, result):
            if result is True:
                self.app.add_background_task(self.stop_node)
        if self.mining_page.mining_status:
            return
        self.main.question_dialog(
            title="Exit app",
            message="Are you sure you want to stop the node and exit the application ?",
            on_result=on_result
        )