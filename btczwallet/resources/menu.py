
import asyncio
import webbrowser
import shutil

from toga import (
    Window, Box, Button
)
from ..framework import Gtk, is_wsl
from toga.style.pack import Pack
from toga.colors import YELLOW, BLACK, GRAY, TRANSPARENT
from toga.constants import (
    COLUMN, ROW, TOP, CENTER, BOLD
)

from .client import Client
from .utils import Utils
from .wallet import Wallet, ImportKey
from .home import Home, Currency
from .txs import Transactions
from .receive import Receive
from .send import Send
from .messages import Messages, EditUser
from .mining import Mining
from .status import AppStatusBar
from .toolbar import AppToolbar
from .storage import Storage
from .settings import Settings

if not is_wsl():
    from .notify import Notify

class Menu(Window):
    def __init__(self):
        super().__init__()

        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.storage = Storage(self.app)
        self.wallet = Wallet(self.app, self)
        self.statusbar = AppStatusBar(self.app, self)
        self.settings = Settings(self.app)

        self.title = "BitcoinZ Wallet"
        self.size = (920,640)
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center
        self.on_close = self.exit_app

        Gtk.Settings.get_default().connect("notify::gtk-theme-name", self.on_change_mode)
        
        self.import_key_toggle = None
        self.import_window_toggle = None
        self.edit_user_toggle = None
        self.currency_toggle = None

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

        self.home_page = Home(self.app, self)
        self.transactions_page = Transactions(self.app, self)
        self.receive_page = Receive(self.app, self)
        self.send_page = Send(self.app, self)
        self.messages_page = Messages(self.app, self)
        self.mining_page = Mining(self.app, self)
        self.toolbar = AppToolbar(self.app, self, self.home_page, self.mining_page)

        self.main_box.add(
            self.toolbar,
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

        self.receive_button = Button(
            text="Receive",
            style=Pack(
                font_weight = BOLD,
                color = GRAY,
                flex = 1,
                padding = (5,0,2,0)
            ),
            on_press=self.receive_button_click
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
            self.receive_button,
            self.send_button,
            self.message_button,
            self.mining_button
        )

        self.home_button_toggle = None
        self.transactions_button_toggle = None
        self.receive_button_toggle = None
        self.send_button_toggle = None
        self.message_button_toggle = None
        self.mining_button_toggle = None
        self.app.add_background_task(self.set_default_page)


    async def set_default_page(self, widget):
        await asyncio.sleep(0.5)
        self.home_button_click(None)
        self.add_actions_cmds()
        try:
            self.statusicon = Notify(self.app, self, self.home_page, self.mining_page)
            self.statusicon.show()
        except Exception:
            pass
        self.app.add_background_task(self.transactions_page.waiting_new_transactions)
        await asyncio.sleep(1)
        await self.messages_page.gather_unread_memos()


    def add_actions_cmds(self):
        if self.settings.notification_txs():
            self.toolbar.notification_txs_cmd.active = True
        else:
            self.toolbar.notification_txs_cmd.active = self.settings.notification_txs()
        if self.settings.notification_messages():
            self.toolbar.notification_messages_cmd.active = True
        else:
            self.toolbar.notification_messages_cmd.active = self.settings.notification_messages()

        self.toolbar.notification_txs_cmd.on_toggled = self.update_notifications_txs
        self.toolbar.notification_messages_cmd.on_toggled = self.update_notifications_messages
        self.toolbar.currency_cmd.action = self.show_currencies_list
        self.toolbar.generate_t_cmd.action = self.new_transparent_address
        self.toolbar.generate_z_cmd.action = self.new_private_address
        self.toolbar.import_key_cmd.action = self.show_import_key
        self.toolbar.edit_username_cmd.action = self.edit_messages_username
        self.toolbar.backup_messages_cmd.action = self.backup_messages
        self.toolbar.check_update_cmd.action = self.check_app_version
        self.toolbar.join_us_cmd.action = self.join_us


    def show_currencies_list(self, action):
        if not self.currency_toggle:
            self.currencies_window = Currency(self)
            self.currencies_window.show()
            self.currency_toggle = True

    def update_notifications_txs(self, action):
        if self.settings.notification_txs():
            self.settings.update_settings("notifications_txs", False)
        else:
            self.settings.update_settings("notifications_txs", True)


    def update_notifications_messages(self, action):
        if self.settings.notification_messages():
            self.settings.update_settings("notifications_messages", False)
        else:
            self.settings.update_settings("notifications_messages", True)


    def new_transparent_address(self, action):
        self.app.add_background_task(self.generate_transparent_address)

    def new_private_address(self, action):
        self.app.add_background_task(self.generate_private_address)


    async def generate_transparent_address(self, widget):
        new_address,_ = await self.commands.getNewAddress()
        if new_address:
            await self.receive_page.update_addresses()
            await self.send_page.update_addresses()
            await self.mining_page.update_addresses()
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address}"
            )


    async def generate_private_address(self, widget):
        new_address,_ = await self.commands.z_getNewAddress()
        if new_address:
            await self.receive_page.update_addresses()
            await self.send_page.update_addresses()
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address}"
            )


    def check_app_version(self, action):
        self.app.add_background_task(self.fetch_repo_info)


    async def fetch_repo_info(self, widget):
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


    def show_import_key(self, action):
        if not self.import_window_toggle:
            self.import_window = ImportKey(self)
            self.import_window.close_button.on_press = self.close_import_key
            self.import_window.show()
            self.import_window_toggle = True
        else:
            self.app.current_window = self.import_window


    async def update_wallet(self):
        self.import_window.close()
        await self.transactions_page.update_transactions()
        await self.receive_page.update_addresses()
        await self.send_page.update_addresses()
        await self.mining_page.update_addresses()
        self.import_key_toggle = None
        self.import_window_toggle = None


    def close_import_key(self, button):
        self.import_window_toggle = None
        self.import_window.close()


    def edit_messages_username(self, action):
        if not self.edit_user_toggle:
            data = self.storage.is_exists()
            if data:
                username = self.storage.get_identity("username")
                if username:
                    self.edit_window = EditUser(username[0], self)
                    self.edit_window.close_button.on_press = self.close_edit_username
                    self.edit_window.show()
                    self.edit_user_toggle = True
        else:
            self.app.current_window = self.edit_window

    
    def close_edit_username(self, button):
        self.edit_user_toggle = None
        self.edit_window.close()


    def backup_messages(self, action):
        def on_result(widget, result):
            if result:
                shutil.copy(self.data, result)
                self.info_dialog(
                    title="Backup Successful!",
                    message=f"Your messages have been successfully backed up to:\n{result}"
                )
        self.data = self.storage.is_exists()
        if self.data:
            self.save_file_dialog(
                title="Save backup to...",
                suggested_filename=self.data,
                file_types=["dat"],
                on_result=on_result
            )


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


    def receive_button_click(self, button):
        self.clear_buttons()
        self.receive_button_toggle = True
        self.receive_button.style.color = BLACK
        self.receive_button.style.background_color = YELLOW
        self.receive_button.on_press = None
        self.pages.add(self.receive_page)
        self.app.add_background_task(self.receive_page.insert_widgets)


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

        elif self.receive_button_toggle:
            self.receive_button_toggle = None
            self.pages.remove(self.receive_page)
            self.receive_button.style.color = GRAY
            self.receive_button.style.background_color = TRANSPARENT
            self.receive_button.on_press = self.receive_button_click
        
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
        self.app.add_background_task(self.receive_page.update_recieve_mode)
        self.app.add_background_task(self.send_page.update_send_mode)
        self.app.add_background_task(self.messages_page.update_messages_mode)
        self.app.add_background_task(self.mining_page.update_mining_mode)
            

    async def stop_node_exit(self, action):
        async def on_result(widget, result):
            if result is True:
                self.home_page.clear_cache()
                await self.commands.stopNode()
                self.app.exit()
                
        if self.mining_page.mining_status:
            return
        self.question_dialog(
            title="Exit app",
            message="Are you sure you want to stop the node and exit the application ?",
            on_result=on_result
        )

    def exit_app(self, action):
        def on_result(widget, result):
            if result is True:
                self.home_page.clear_cache()
                self.app.exit()
        if self.mining_page.mining_status:
            return
        self.question_dialog(
            title="Exit app",
            message="Are you sure you want to exit the application ?",
            on_result=on_result
        )