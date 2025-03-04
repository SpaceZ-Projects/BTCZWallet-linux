
import asyncio

from toga import (
    MainWindow, Box, Button
)
from toga.style.pack import Pack
from toga.colors import WHITE, YELLOW, BLACK, GRAY
from toga.constants import (
    COLUMN, ROW, TOP, CENTER, BOLD
)

from .client import Client
from .utils import Utils
from .wallet import Wallet
from .home import Home
from .txs import Transactions
from .recieve import Recieve
from .send import Send
from .status import AppStatusBar
from .toolbar import AppToolbar

class Menu(MainWindow):
    def __init__(self):
        super().__init__()

        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.wallet = Wallet(self.app)
        self.statusbar = AppStatusBar(self.app)

        self.title = "BitcoinZ Wallet"
        self.size = (900,600)
        
        self._is_minimized = None
        
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self.on_close = self.on_close_menu

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )
        self.menu_bar = Box(
            style=Pack(
                direction = ROW,
                alignment = TOP,
                height = 45,
                flex = 1,
                padding = (0,4,5,4)
            )
        )
        self.pages = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1
            )
        )

        self.home_page = Home(self.app)
        self.transactions_page = Transactions(self.app, self)
        self.recieve_page = Recieve(self.app, self)
        self.send_page = Send(self.app, self)

        self.main_box.add(
            self.wallet,
            self.menu_bar,
            self.pages,
            self.statusbar
        )

        self.content = self.main_box
        
        self.insert_toolbar()

    def insert_toolbar(self):
        self.app.commands.clear()
        self.apptoolbar = AppToolbar(self.app)
        self.apptoolbar.exit_cmd.action = self.on_close_menu
        self.insert_menu_buttons()

    def insert_menu_buttons(self):
        self.home_button = Button(
            text="Home",
            style=Pack(
                font_weight = BOLD,
                color = GRAY,
                flex = 1,
                padding = (5,0,2,5)
            ),
            on_press=self.home_button_click
        )

        self.transactions_button = Button(
            text="Transactions",
            style=Pack(
                font_weight = BOLD,
                color = GRAY,
                flex = 1,
                padding = (5,0,2,0)
            ),
            on_press=self.transactions_button_click
        )

        self.recieve_button = Button(
            text="Recieve",
            style=Pack(
                font_weight = BOLD,
                color = GRAY,
                flex = 1,
                padding = (5,0,2,0)
            ),
            on_press=self.recieve_button_click
        )

        self.send_button = Button(
            text="Send",
            style=Pack(
                font_weight = BOLD,
                color = GRAY,
                flex = 1,
                padding = (5,0,2,0)
            ),
            on_press=self.send_button_click
        )

        self.message_button = Button(
            text="Messages",
            style=Pack(
                font_weight = BOLD,
                color = GRAY,
                flex = 1,
                padding = (5,0,2,0)
            ),
            on_press=self.message_button_click
        )
        
        self.mining_button = Button(
            text="Mining",
            style=Pack(
                font_weight = BOLD,
                color = GRAY,
                flex = 1,
                padding = (5,5,2,0)
            ),
            on_press=self.mining_button_click
        )

        self.menu_bar.add(
            self.home_button,
            self.transactions_button,
            self.recieve_button,
            self.send_button,
            self.message_button,
            self.mining_button
        )

        self.home_button_toggle = None
        self.transactions_button_toggle = None
        self.recieve_button_toggle = None
        self.send_button_toggle = None
        self.message_button_toggle = None
        self.mining_button_toggle = None
        self.app.add_background_task(self.set_default_page)


    async def set_default_page(self, widget):
        await asyncio.sleep(0.5)
        self.home_button_click(None)
        self.app.add_background_task(self.transactions_page.update_transactions)


    def home_button_click(self, button):
        self.clear_buttons()
        self.home_button_toggle = True
        self.home_button.style.color = BLACK
        self.home_button.style.background_color = YELLOW
        self.home_button.on_press = None
        self.pages.add(self.home_page)
        self.app.add_background_task(self.home_page.insert_widgets)


    def transactions_button_click(self, button):
        self.clear_buttons()
        self.transactions_button_toggle = True
        self.transactions_button.style.color = BLACK
        self.transactions_button.style.background_color = YELLOW
        self.transactions_button.on_press = None
        self.pages.add(self.transactions_page)
        self.app.add_background_task(self.transactions_page.insert_widgets)


    def recieve_button_click(self, button):
        self.clear_buttons()
        self.recieve_button_toggle = True
        self.recieve_button.style.color = BLACK
        self.recieve_button.style.background_color = YELLOW
        self.recieve_button.on_press = None
        self.pages.add(self.recieve_page)
        self.app.add_background_task(self.recieve_page.insert_widgets)


    def send_button_click(self, button):
        self.clear_buttons()
        self.send_button_toggle = True
        self.send_button.style.color = BLACK
        self.send_button.style.background_color = YELLOW
        self.send_button.on_press = None
        self.pages.add(self.send_page)
        self.app.add_background_task(self.send_page.insert_widgets)

    
    def message_button_click(self, button):
        self.clear_buttons()
        self.message_button_toggle = True
        self.message_button.style.color = BLACK
        self.message_button.style.background_color = YELLOW
        self.message_button.on_press = None


    def mining_button_click(self, button):
        self.clear_buttons()
        self.mining_button_toggle = True
        self.mining_button.style.color = BLACK
        self.mining_button.style.background_color = YELLOW
        self.mining_button.on_press = None


    def clear_buttons(self):
        if self.home_button_toggle:
            self.home_button_toggle = None
            self.pages.remove(self.home_page)
            self.home_button.style.color = GRAY
            self.home_button.style.background_color = WHITE
            self.home_button.on_press = self.home_button_click

        elif self.transactions_button_toggle:
            self.transactions_button_toggle = None
            self.pages.remove(self.transactions_page)
            self.transactions_button.style.color = GRAY
            self.transactions_button.style.background_color = WHITE
            self.transactions_button.on_press = self.transactions_button_click

        elif self.recieve_button_toggle:
            self.recieve_button_toggle = None
            self.pages.remove(self.recieve_page)
            self.recieve_button.style.color = GRAY
            self.recieve_button.style.background_color = WHITE
            self.recieve_button.on_press = self.recieve_button_click
        
        elif self.send_button_toggle:
            self.send_button_toggle = None
            self.pages.remove(self.send_page)
            self.send_button.style.color = GRAY
            self.send_button.style.background_color = WHITE
            self.send_button.on_press = self.send_button_click

        elif self.message_button_toggle:
            self.message_button_toggle = None
            self.message_button.style.color = GRAY
            self.message_button.style.background_color = WHITE
            self.message_button.on_press = self.message_button_click

        elif self.mining_button_toggle:
            self.mining_button_toggle = None
            self.mining_button.style.color = GRAY
            self.mining_button.style.background_color = WHITE
            self.mining_button.on_press = self.message_button_click
            

    def on_close_menu(self, widget):
        self.app.exit()