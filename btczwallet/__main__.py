
from toga import (
    App, Window, Box, ImageView, Label
)
from .framework import Gtk, Gdk
from toga.colors import GRAY, YELLOW
from toga.style.pack import Pack
from toga.constants import RIGHT, BOLD, COLUMN, ROW, LEFT

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
        self.app_version._impl.native.set_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.app_version._impl.native.set_has_window(True)
        self.app_version._impl.native.connect("enter-notify-event", self.app_version_mouse_enter)
        self.app_version._impl.native.connect("leave-notify-event", self.app_version_mouse_leave)

        self.tor_icon = ImageView(
            image="images/tor_off.png",
            style=Pack(
                padding_left = 10,
            )
        )

        self.network_status = Label(
            text="",
            style=Pack(
                text_align = LEFT,
                font_weight = BOLD,
                padding_left = 10,
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
            self.tor_icon,
            self.network_status,
            self.app_version
        )
        self.content = self.startup_panel


    def on_change_mode(self, settings, param_spec):
        self.startup.update_setup_mode()

    def app_version_mouse_enter(self, widget, event):
        self.app_version.style.color = YELLOW

    def app_version_mouse_leave(self, widget, event):
        self.app_version.style.color = GRAY


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
        version = "1.0.8"
    )
    return app

if __name__ == "__main__":
    app = main()
    app.main_loop()
