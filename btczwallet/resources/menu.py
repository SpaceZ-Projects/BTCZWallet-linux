
import asyncio
import webbrowser

from toga import (
    MainWindow, Box, Button
)
from ..framework import Gtk, is_wsl
from toga.style.pack import Pack
from toga.colors import YELLOW, BLACK, GRAY, TRANSPARENT
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
from .messages import Messages, EditUser
from .mining import Mining
from .status import AppStatusBar
from .toolbar import AppToolbar
from .storage import Storage

if not is_wsl():
    from .notify import Notify

class Menu(MainWindow):
    def __init__(self):
        super().__init__()

        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.storage = Storage(self.app)
        self.wallet = Wallet(self.app)
        self.statusbar = AppStatusBar(self.app)

        self.title = "BitcoinZ Wallet"
        self.size = (900,640)
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self.on_close = self.exit_app

        Gtk.Settings.get_default().connect("notify::gtk-theme-name", self.on_change_mode)

        self.edit_user_toggle = None

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
        self.messages_page = Messages(self.app, self)
        self.mining_page = Mining(self.app, self)

        self.main_box.add(
            self.wallet,
            self.menu_bar,
            self.pages,
            self.statusbar
        )

        self.content = self.main_box
        
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
        self.add_actions_cmds()
        try:
            self.statusicon = Notify(self.app, self.home_page, self.mining_page)
            self.statusicon.show()
        except Exception:
            pass
        self.app.add_background_task(self.transactions_page.update_transactions)
        await asyncio.sleep(1)
        await self.messages_page.gather_unread_memos()


    def add_actions_cmds(self):
        self.app.commands.clear()
        self.apptoolbar = AppToolbar(self.app)
        self.apptoolbar.exit_cmd.action = self.exit_app
        self.apptoolbar.stop_exit_cmd.action = self.stop_node_exit
        self.apptoolbar.generate_t_cmd.action = self.generate_transparent_address
        self.apptoolbar.generate_z_cmd.action = self.generate_private_address
        self.apptoolbar.edit_username_cmd.action = self.edit_messages_username
        self.apptoolbar.check_update_cmd.action = self.check_app_version
        self.apptoolbar.join_us_cmd.action = self.join_us


    async def generate_transparent_address(self, action):
        new_address = await self.commands.getNewAddress()
        if new_address:
            if self.recieve_page.transparent_toggle:
                self.insert_new_address(new_address[0])
            if self.send_page.transparent_toggle:
                await self.send_page.update_send_options(None)
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address[0]}"
            )


    async def generate_private_address(self, widget):
        new_address = await self.commands.z_getNewAddress()
        if new_address:
            if self.recieve_page.private_toggle:
                self.insert_new_address(new_address[0])
            if self.send_page.private_toggle:
                await self.send_page.update_send_options(None)
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address[0]}"
            )


    def insert_new_address(self, address):
        self.recieve_page.addresses_table.data.insert(
            0, address
        )


    async def check_app_version(self, widget):
        def on_result(widget, result):
            if result is True:
                webbrowser.open(self.git_link)
        git_version, link = await self.utils.get_repo_info()
        if git_version:
            self.git_link = link
            current_version = self.app.version
            if git_version == current_version:
                self.info_dialog(
                    title="Check updates",
                    message=f"Current version: {current_version}\nThe app version is up to date."
                )
            else:
                self.question_dialog(
                    title="Check updates",
                    message=f"Current version: {current_version}\nGit version: {git_version}\nWould you like to update the app ?",
                    on_result=on_result
                )


    def edit_messages_username(self, action):
        if not self.edit_user_toggle:
            data = self.storage.is_exists()
            if data:
                username = self.storage.get_identity("username")
                if username:
                    self.edit_window = EditUser(username[0], self)
                    self.edit_window.on_close = self.close_edit_username
                    self.edit_window.close_button.on_press = self.close_edit_username
                    self.edit_window.show()
                    self.edit_user_toggle = True

    
    def close_edit_username(self, button):
        self.edit_user_toggle = None
        self.edit_window.close()


    def join_us(self, action):
        discord = "https://discord.com/invite/aAU2WeJ"
        webbrowser.open(discord)


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
        self.pages.add(self.messages_page)
        self.app.add_background_task(self.messages_page.insert_widgets)


    def mining_button_click(self, button):
        self.clear_buttons()
        self.mining_button_toggle = True
        self.mining_button.style.color = BLACK
        self.mining_button.style.background_color = YELLOW
        self.mining_button.on_press = None
        self.pages.add(self.mining_page)
        self.app.add_background_task(self.mining_page.insert_widgets)


    def clear_buttons(self):
        if self.home_button_toggle:
            self.home_button_toggle = None
            self.pages.remove(self.home_page)
            self.home_button.style.color = GRAY
            self.home_button.style.background_color = TRANSPARENT
            self.home_button.on_press = self.home_button_click

        elif self.transactions_button_toggle:
            self.transactions_button_toggle = None
            self.pages.remove(self.transactions_page)
            self.transactions_button.style.color = GRAY
            self.transactions_button.style.background_color = TRANSPARENT
            self.transactions_button.on_press = self.transactions_button_click

        elif self.recieve_button_toggle:
            self.recieve_button_toggle = None
            self.pages.remove(self.recieve_page)
            self.recieve_button.style.color = GRAY
            self.recieve_button.style.background_color = TRANSPARENT
            self.recieve_button.on_press = self.recieve_button_click
        
        elif self.send_button_toggle:
            self.send_button_toggle = None
            self.pages.remove(self.send_page)
            self.send_button.style.color = GRAY
            self.send_button.style.background_color = TRANSPARENT
            self.send_button.on_press = self.send_button_click

        elif self.message_button_toggle:
            self.message_button_toggle = None
            self.pages.remove(self.messages_page)
            self.message_button.style.color = GRAY
            self.message_button.style.background_color = TRANSPARENT
            self.message_button.on_press = self.message_button_click

        elif self.mining_button_toggle:
            self.mining_button_toggle = None
            self.pages.remove(self.mining_page)
            self.mining_button.style.color = GRAY
            self.mining_button.style.background_color = TRANSPARENT
            self.mining_button.on_press = self.mining_button_click


    def on_change_mode(self, settings, param_spec):
        self.app.add_background_task(self.wallet.update_wallet_mode)
        self.app.add_background_task(self.home_page.update_home_mode)
        self.app.add_background_task(self.recieve_page.update_recieve_mode)
        self.app.add_background_task(self.send_page.update_send_mode)
        self.app.add_background_task(self.messages_page.update_messages_mode)
        self.app.add_background_task(self.mining_page.update_mining_mode)
            

    async def stop_node_exit(self, action):
        if self.mining_page.mining_status:
            return
        self.home_page.clear_cache()
        await self.commands.stopNode()
        self.app.exit()

    def exit_app(self, action):
        if self.mining_page.mining_status:
            return
        self.home_page.clear_cache()
        self.app.exit()