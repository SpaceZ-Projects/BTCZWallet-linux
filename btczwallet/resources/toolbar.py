
from toga import App, Window, Box
from ..framework import Toolbar, Command, CheckCommand

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

        self.about_cmd = Command(
            title="About",
            action=self.display_about_dialog
        )
        self.exit_cmd = Command(
            title="Exit",
            action=self.exit_app
        )
        self.stop_exit_cmd = Command(
            title="Stop node",
            action=self.stop_node_exit
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
            title="Currency"
        )

        self.notification_txs_cmd = CheckCommand(
            title="Notifications txs"
        )

        self.notification_messages_cmd = CheckCommand(
            title="Notifications messages"
        )

        self.startup_cmd = CheckCommand(
            title="Run on startup"
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
            title="Peer info"
        )

        self.network_menu = Command(
            title="Network",
            sub_commands=[
                self.peer_info_cmd
            ]
        )

        self.generate_t_cmd = Command(
            title="Transparent address"
        )

        self.generate_z_cmd = Command(
            title="Private address"
        )

        self.generate_address_cmd = Command(
            title="Generate address",
            sub_commands=[
                self.generate_t_cmd,
                self.generate_z_cmd
            ]
        )

        self.import_key_cmd = Command(
            title="Import private key"
        )
        self.export_wallet_cmd = Command(
            title="Export wallet"
        )
        self.import_wallet_cmd = Command(
            title="Import wallet"
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
            title="Edit username"
        )
        self.backup_messages_cmd = Command(
            title="Backup messages"
        )

        self.messages_menu = Command(
            title="Messages",
            sub_commands=[
                self.edit_username_cmd,
                self.backup_messages_cmd
            ]
        )

        self.check_update_cmd = Command(
            title="Check update"
        )

        self.join_us_cmd = Command(
            title="Join us"
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

    async def stop_node(self, widget):
        self.home_page.bitcoinz_curve.image = None
        self.home_page.clear_cache()
        await self.commands.stopNode()
        self.app.exit()
