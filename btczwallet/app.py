
from toga import (
    App, Window, Box, ImageView, Label
)
from .framework import Gtk
from toga.colors import GRAY
from toga.style.pack import Pack
from toga.constants import RIGHT, BOLD, COLUMN, ROW

from .resources import BTCZSetup, Utils

class BitcoinZGUI(Window):
    def __init__(self):
        super().__init__(
            size=(350, 400),
            resizable=False,
            minimizable = False
        )

        self.utils = Utils(self.app)

        self.title = "BitcoinZ Wallet"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        Gtk.Settings.get_default().connect("notify::gtk-theme-name", self.on_change_mode)

        self.startup_panel = Box(
            style=Pack(
                direction= COLUMN,
                flex = 10
            )
        )
        self.bitcoinz_logo = ImageView(
            image="images/BitcoinZ.png",
            style=Pack(
                padding_top = 22,
                flex = 8
            )
        )
        self.version_box = Box(
            style=Pack(
                direction = ROW
            )
        )
        self.empty_box = Box(
            style=Pack(
                flex = 9
            )
        )
        self.app_version = Label(
            text=f"v{self.app.version}",
            style=Pack(
                color = GRAY,
                text_align = RIGHT,
                font_weight = BOLD,
                padding_right = 10,
                font_size = 10,
                flex = 1
            )
        )
        self.startup = BTCZSetup(
            self.app,
            self
        )
        self.startup_panel.add(
            self.bitcoinz_logo,
            self.version_box,
            self.startup
        )
        self.version_box.add(
            self.empty_box,
            self.app_version
        )
        self.content = self.startup_panel


    def on_change_mode(self, settings, param_spec):
        self.startup.update_setup_mode()


class BitcoinZWallet(App):
    def startup(self):
        
        self.main_window = BitcoinZGUI()
        self.main_window.show()


def main():
    app = BitcoinZWallet(
        icon="images/BitcoinZ",
        formal_name = "BTCZWallet",
        app_id = "com.btcz",
        home_page = "https://getbtcz.com",
        author = "BTCZCommunity",
        version = "1.0.4"
    )
    return app

if __name__ == "__main__":
    app = main()
    app.main_loop()
