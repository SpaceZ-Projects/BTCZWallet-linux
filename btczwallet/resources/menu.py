
import asyncio
import webbrowser
import shutil
from datetime import datetime

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
from .wallet import Wallet, ImportKey, ImportWallet
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
from .network import Peer, AddNode

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
        self.on_close = self.on_close_menu

        Gtk.Settings.get_default().connect("notify::gtk-theme-name", self.on_change_mode)
        
        self._is_hidden = None
        self.import_key_toggle = None
        self.peer_toggle = None

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
        self.app.add_background_task(self.transactions_page.update_transactions)
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
        if self.settings.minimize_to_tray():
            self.toolbar.minimize_cmd.active = True
        else:
            self.toolbar.minimize_cmd.active = self.settings.minimize_to_tray()
        if self.settings.startup():
            self.toolbar.startup_cmd.active = True
        else:
            self.toolbar.startup_cmd.active = self.settings.startup()

        self.toolbar.currency_cmd.action = self.show_currencies_list
        self.toolbar.notification_txs_cmd.on_toggled = self.update_notifications_txs
        self.toolbar.notification_messages_cmd.on_toggled = self.update_notifications_messages
        self.toolbar.minimize_cmd.on_toggled = self.update_minimize_to_tray
        self.toolbar.startup_cmd.on_toggled = self.update_app_startup
        self.toolbar.peer_info_cmd.action = self.show_peer_info
        self.toolbar.add_node_cmd.action = self.show_add_node
        self.toolbar.generate_t_cmd.action = self.new_transparent_address
        self.toolbar.generate_z_cmd.action = self.new_private_address
        self.toolbar.import_key_cmd.action = self.show_import_key
        self.toolbar.export_wallet_cmd.action = self.export_wallet
        self.toolbar.import_wallet_cmd.action = self.show_import_wallet
        self.toolbar.edit_username_cmd.action = self.edit_messages_username
        self.toolbar.backup_messages_cmd.action = self.backup_messages
        self.toolbar.check_update_cmd.action = self.check_app_version
        self.toolbar.join_us_cmd.action = self.join_us


    def show_currencies_list(self, action):
        self.currencies_window = Currency(self)
        self.currencies_window.show()


    def show_peer_info(self, action):
        if not self.peer_toggle:
            peer_window = Peer(self)
            peer_window.show()
            self.peer_window = peer_window
            self.peer_toggle = True
        else:
            self.app.current_window = self.peer_window

    def show_add_node(self, action):
        self.add_node_window = AddNode()
        self.add_node_window.show()

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


    def update_minimize_to_tray(self, action):
        if self.settings.minimize_to_tray():
            self.settings.update_settings("minimize", False)
        else:
            self.settings.update_settings("minimize", True)


    def update_app_startup(self, action):
        if self.settings.startup():
            reg = self.utils.remove_from_startup()
            self.settings.update_settings("startup", False)
        else:
            reg = self.utils.add_to_startup()
            if reg:
                self.settings.update_settings("startup", True)
            else:
                self.toolbar.startup_cmd.active = False


    def new_transparent_address(self, action):
        self.app.add_background_task(self.generate_transparent_address)

    def new_private_address(self, action):
        self.app.add_background_task(self.generate_private_address)


    async def generate_transparent_address(self, widget):
        async def on_result(widget, result):
            if result is None:
                if self.receive_page.transparent_toggle:
                    self.insert_new_address(new_address)
                if self.send_page.transparent_toggle:
                    await self.send_page.reload_addresses()
        new_address,_ = await self.commands.getNewAddress()
        if new_address:
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address}",
                on_result=on_result
            )


    async def generate_private_address(self, widget):
        async def on_result(widget, result):
            if result is None:
                if self.receive_page.private_toggle:
                    self.insert_new_address(new_address)
                if self.send_page.private_toggle:
                    await self.send_page.reload_addresses()
        new_address,_ = await self.commands.z_getNewAddress()
        if new_address:
            self.info_dialog(
                title="New Address",
                message=f"Generated address : {new_address}",
                on_result=on_result
            )


    def insert_new_address(self, address):
        self.receive_page.addresses_table.data.insert(
            index=0,
            data=address
        )


    def check_app_version(self, action):
        self.app.add_background_task(self.fetch_repo_info)


    async def fetch_repo_info(self, widget):
        def on_result(widget, result):
            if result is True:
                webbrowser.open(self.git_link)
        tor_enabled = self.settings.tor_network()
        git_version, link = await self.utils.get_repo_info(tor_enabled)
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
        self.import_window = ImportKey(self)
        self.import_window.show()


    def export_wallet(self, action):
        def on_result(widget, result):
            if result is True:
                self.set_export_dir()
        export_dir = self.utils.verify_export_dir()
        if export_dir:
            self.app.add_background_task(self.run_export_wallet)
        else:
            self.question_dialog(
                title="Missing Export Dir",
                message="The '-exportdir' option is not configured in your bitcoinz.conf file.\n"
                        "Would you like to configure it ?",
                on_result=on_result
            )

    
    def set_export_dir(self):
        def on_result(widget, result):
            if result is not None:
                self.utils.update_config(result)
                self.question_dialog(
                    title="Export Directory Set",
                    message="Your export folder has been successfully saved. Would you like to restart your node now to apply this change?",
                    on_result=self.restart_node
                )
        self.select_folder_dialog(
            title="Select Folder",
            on_result=on_result
        )


    async def restart_node(self, widget, result):
        if result is True:
            restart = self.utils.restart_app()
            if restart:
                await self.commands.stopNode()
                self.app.exit()


    async def run_export_wallet(self, widget):
        file_name = f"wallet{datetime.today().strftime('%d%m%Y%H%M%S')}"
        exported_file, error_message = await self.commands.z_ExportWallet(file_name)
        if exported_file and error_message is None:
            self.info_dialog(
                title="Wallet Exported Successfully",
                message=f"Your wallet has been exported as '{exported_file}'."
            )

    def show_import_wallet(self, action):
        self.import_window = ImportWallet(self)
        self.import_window.show()


    def edit_messages_username(self, action):
        data = self.storage.is_exists()
        if data:
            username = self.storage.get_identity("username")
            if username:
                self.edit_window = EditUser(username[0], self)
                self.edit_window.show()


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
        self.app.add_background_task(self.toolbar.set_toolbar_icons)
        self.app.add_background_task(self.wallet.update_wallet_mode)
        self.app.add_background_task(self.home_page.update_home_mode)
        self.app.add_background_task(self.transactions_page.update_transactions_mode)
        self.app.add_background_task(self.send_page.update_send_mode)
        self.app.add_background_task(self.receive_page.update_receive_mode)
        self.app.add_background_task(self.messages_page.update_messages_mode)
        self.app.add_background_task(self.mining_page.update_mining_mode)


    def on_close_menu(self, widget):
        if self.settings.minimize_to_tray():
            self.hide()
            self._is_hidden = True
            return
        self.toolbar.exit_app(None)