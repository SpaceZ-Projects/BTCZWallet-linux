
from toga import App, Group, Command


class AppToolbar():
    def __init__(self, app:App):
        self.app = app

        self.app_menu = Group(
            text="App",
            order = 0
        )

        self.about_cmd = Command(
            text="About",
            group=self.app_menu,
            order=0,
            action=self.display_about_dialog
        )

        self.exit_cmd = Command(
            text="Exit",
            group=self.app_menu,
            order=1,
            action=True
        )

        self.stop_exit_cmd = Command(
            text="Stop node",
            group=self.app_menu,
            order=2,
            action=True
        )

        self.wallet_menu = Group(
            text="Wallet",
            order=1
        )

        self.generate_address_cmd = Group(
            text="Generate address",
            parent=self.wallet_menu,
            order=0
        )

        self.generate_t_cmd = Command(
            text="Transparent address",
            group=self.generate_address_cmd,
            action=True,
            order=0
        )

        self.generate_z_cmd = Command(
            text="Private address",
            group=self.generate_address_cmd,
            action=True,
            order=1
        )

        self.messages_menu = Group(
            text="Messages",
            order=2
        )

        self.edit_username_cmd = Command(
            text="Edit username",
            group=self.messages_menu,
            action=True
        )

        self.help_menu = Group(
            text="Help",
            order=3
        )

        self.check_update_cmd = Command(
            text="Check update",
            group=self.help_menu,
            order=0,
            action=True
        )

        self.join_us_cmd = Command(
            text="Join us",
            group=self.help_menu,
            order=1,
            action=True
        )

        self.app.commands.add(
            self.about_cmd,
            self.exit_cmd,
            self.stop_exit_cmd,
            self.generate_t_cmd,
            self.generate_z_cmd,
            self.edit_username_cmd,
            self.check_update_cmd,
            self.join_us_cmd
        )


    def display_about_dialog(self, action):
        self.app.about()
