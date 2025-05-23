
import psutil

from toga import App, Window
from ..framework import StatusIconGtk, Gtk, Command

from .client import Client


class Notify(StatusIconGtk):
    def __init__(self, app:App, main:Window, home_page, mining_page):
        super().__init__(
            icon = "images/BitcoinZ-32.png",
            on_right_click=self.notify_on_click,
            on_left_click=self.show_menu
        )

        self.app = app
        self.main = main
        self.home_page = home_page
        self.mining_page = mining_page

        self.commands = Client(self.app)

    def notify_on_click(self, button, time):
        menu = Gtk.Menu()
        
        stop_exit_cmd = Command(
            title="Stop node",
            action=self.stop_node_exit
        )

        exit_cmd = Command(
            title="Exit",
            action=self.exit_app
        )

        menu.append(stop_exit_cmd)
        menu.append(exit_cmd)
        menu.show_all()

        menu.popup(None, None, None, None, button, time)

    
    def show_menu(self):
        if self.main.import_key_toggle:
            return
        self.app.current_window = self.main


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


    def stop_tor(self):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "tor_binary":
                    proc.kill()
        except Exception as e:
            pass


    def stop_node_exit(self, action):
        async def on_result(widget, result):
            if result is True:
                self.home_page.bitcoinz_curve.image = None
                self.home_page.clear_cache()
                self.stop_tor()
                await self.commands.stopNode()
                self.app.exit()
        if self.mining_page.mining_status:
            return
        self.main.question_dialog(
            title="Exit app",
            message="Are you sure you want to stop the node and exit the application ?",
            on_result=on_result
        )