
import psutil

from toga import App, Window
from ..framework import StatusIconGtk, Command, Menu

from .client import Client


class Notify(StatusIconGtk):
    def __init__(self, app:App, main:Window, home_page, mining_page):
        super().__init__(
            icon = "images/BitcoinZ-32.png",
            on_right_click=self._on_right_click,
            on_left_click=self._on_left_click,
            on_double_click=self._on_double_click
        )

        self.app = app
        self.main = main
        self.home_page = home_page
        self.mining_page = mining_page

        self.commands = Client(self.app)

        self.menu = Menu()
        
        stop_exit_cmd = Command(
            title="Stop node",
            action=self.stop_node_exit,
            icon="images/stop.png"
        )

        exit_cmd = Command(
            title="Exit",
            action=self.exit_app,
            icon="images/exit.png"
        )

        self.menu.add_commands(
            [
                stop_exit_cmd,
                exit_cmd
            ]
        )


    def _on_right_click(self):
        self.menu.popup_at_pointer(None)


    def _on_left_click(self):
        if not self.main._is_hidden:
            self.main._impl.native.present()

    
    def _on_double_click(self):
        if self.main._is_hidden:
            self.main.position = self.main.position
            self.main.show()
            self.main._is_hidden = None


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