
import psutil

from toga import App, Window, Box
from ..framework import Toolbar, Command, CheckCommand, Gtk

from toga.style.pack import Pack
from toga.constants import TOP, ROW

from .client import Client


class AppToolbar(Box):
    def __init__(self, app:App, main:Window, home_page ,mining_page):
        super().__init__(
            style=Pack(
                direction = ROW,
                height = 24,
                alignment = TOP
            )
        )
        self.app = app
        self.main = main
        self.home_page = home_page
        self.mining_page = mining_page
        self.commands = Client(self.app)

        self.toolbar = Toolbar()

        accel_group = Gtk.AccelGroup()
        self.main._impl.native.add_accel_group(accel_group)

        self.about_cmd = Command(
            title="About",
            action=self.display_about_dialog,
            tooltip="Information about this application"
        )
        self.exit_cmd = Command(
            title="Exit",
            action=self.exit_app,
            tooltip="Exit the application and keep node running in background",
            shortcut="<Alt>F4",
            accel_group=accel_group
        )
        self.stop_exit_cmd = Command(
            title="Stop node",
            action=self.stop_node_exit,
            tooltip="Stop the node and exit the application",
            shortcut="<Alt>Q",
            accel_group=accel_group
        )

        self.app_menu = Command(
            title="App",
            sub_commands=[
                self.about_cmd,
                self.exit_cmd,
                self.stop_exit_cmd
            ]
        )

        self.currency_cmd = Command(
            title="Currency",
            tooltip="Change your currency display",
            shortcut="<Control><Shift>C",
            accel_group=accel_group
        )

        self.notification_txs_cmd = CheckCommand(
            title="Notifications txs",
            tooltip="Enable/Disable the transactions notifications"
        )

        self.notification_messages_cmd = CheckCommand(
            title="Notifications messages",
            tooltip="Enable/Disable the messages notifications"
        )

        self.startup_cmd = CheckCommand(
            title="Run on startup",
            tooltip="Enable/Disable app startup on boot"
        )

        self.settings_menu = Command(
            title="Settings",
            sub_commands=[
                self.currency_cmd,
                self.notification_txs_cmd,
                self.notification_messages_cmd,
                self.startup_cmd
            ]
        )

        self.peer_info_cmd = Command(
            title="Peer info",
            tooltip="Display data about each node connected",
            shortcut="<Control><Shift>N",
            accel_group=accel_group
        )
        self.add_node_cmd = Command(
            title="Add node",
            tooltip="add a node to the addnode list"
        )

        self.network_menu = Command(
            title="Network",
            sub_commands=[
                self.peer_info_cmd,
                self.add_node_cmd
            ]
        )

        self.generate_t_cmd = Command(
            title="Transparent address (T)",
            tooltip="Generate a new transparent (T) address"
        )

        self.generate_z_cmd = Command(
            title="Shielded address (Z)",
            tooltip="Generate a new shielded (Z) address"
        )

        self.generate_address_cmd = Command(
            title="Generate address",
            sub_commands=[
                self.generate_t_cmd,
                self.generate_z_cmd
            ]
        )

        self.import_key_cmd = Command(
            title="Import private key",
            tooltip="Import a private key into your wallet"
        )
        self.export_wallet_cmd = Command(
            title="Export wallet",
            tooltip="Export your wallet data to a file"
        )
        self.import_wallet_cmd = Command(
            title="Import wallet",
            tooltip="Import a wallet from a file"
        )

        self.wallet_menu = Command(
            title="Wallet",
            sub_commands=[
                self.generate_address_cmd,
                self.import_key_cmd,
                self.export_wallet_cmd,
                self.import_wallet_cmd
            ]
        )

        self.edit_username_cmd = Command(
            title="Edit username",
            tooltip="Change your messaging username"
        )
        self.backup_messages_cmd = Command(
            title="Backup messages",
            tooltip="Backup your messages to a file"
        )

        self.messages_menu = Command(
            title="Messages",
            sub_commands=[
                self.edit_username_cmd,
                self.backup_messages_cmd
            ]
        )

        self.check_update_cmd = Command(
            title="Check update",
            tooltip="Check for application updates"
        )

        self.join_us_cmd = Command(
            title="Join us",
            tooltip="Join our community on Discord"
        )

        self.help_menu = Command(
            title="Help",
            sub_commands=[
                self.check_update_cmd,
                self.join_us_cmd
            ]
        )

        self.toolbar.add_command(
            [
                self.app_menu,
                self.settings_menu,
                self.network_menu,
                self.wallet_menu,
                self.messages_menu,
                self.help_menu
            ]
        )

        self._impl.native.pack_start(self.toolbar, True, True, 0)


    def display_about_dialog(self, action):
        self.app.about()

    def exit_app(self, action):
        def on_result(widget, result):
            if result is True:
                self.home_page.bitcoinz_curve.image = None
                self.home_page.clear_cache()
                self.app.exit()
        if self.mining_page.mining_status:
            return
        self.main.question_dialog(
            title="Exit app",
            message="Are you sure you want to exit the application ?",
            on_result=on_result
        )

    def stop_node_exit(self, action):
        async def on_result(widget, result):
            if result is True:
                await self.stop_node()

        if self.mining_page.mining_status:
            return
        self.main.question_dialog(
            title="Exit app",
            message="Are you sure you want to stop the node and exit the application ?",
            on_result=on_result
        )

    def stop_tor(self):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "tor_binary":
                    proc.kill()
        except Exception as e:
            pass

    async def stop_node(self):
        self.home_page.bitcoinz_curve.image = None
        self.home_page.clear_cache()
        self.stop_tor()
        await self.commands.stopNode()
        self.app.exit()
