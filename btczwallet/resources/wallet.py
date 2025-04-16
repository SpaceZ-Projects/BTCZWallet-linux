
import asyncio
import json

from toga import (
    App, Window, Box, Label, ImageView,
    Button, TextInput
)
from toga.style.pack import Pack
from toga.colors import rgb, GRAY, RED
from toga.constants import (
    TOP, ROW, LEFT, BOLD, COLUMN,
    RIGHT, CENTER, BOTTOM
)

from .client import Client
from .utils import Utils
from .units import Units

class Wallet(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                height = 120,
                alignment = TOP,
                padding =5
            )
        )

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.units = Units(self.app)

        self.unconfirmed_balance_toggle = None
        mode = self.utils.get_sys_mode()
        if mode:
            background_color = rgb(56, 56, 56)
        else:
            background_color = rgb(230,230,230)

        self.bitcoinz_logo = ImageView(
            image="images/BTCZ.png",
            style=Pack(
                width=100,
                height=100,
                padding_top = 10,
                padding_left = 10
            )
        )
        self.bitcoinz_title = Label(
            text="Full Node Wallet",
            style=Pack(
                color = GRAY,
                font_size = 20,
                font_weight = BOLD,
                text_align = LEFT,
                flex = 1,
                padding_top = 40
            )
        )
        self.balances_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = background_color,
                padding = 10,
                alignment = RIGHT,
                width = 350
            )
        )
        self.total_balances_label = Label(
            text="Total Balances",
            style=Pack(
                font_size = 13,
                font_weight = BOLD,
                text_align = CENTER,
                color = GRAY,
                padding_top = 5,
                flex =1
            )
        )
        self.total_value = Label(
            text="",
            style=Pack(
                font_size = 13,
                font_weight = BOLD,
                text_align = CENTER,
                padding_top = 5
            )
        )
        self.balances_type_box = Box(
            style=Pack(
                direction = ROW,
                alignment = BOTTOM,
                flex = 1
            )
        )

        self.transparent_balance_box = Box(
            style=Pack(
                direction = COLUMN,
                padding = 5,
                flex = 1
            )
        )
        self.private_balance_box = Box(
            style=Pack(
                direction = COLUMN,
                padding = 5,
                flex = 1
            )
        )

        self.transparent_label = Label(
            text="Transparent",
            style=Pack(
                text_align = CENTER,
                color = GRAY,
                font_weight = BOLD
            )
        )

        self.transparent_value = Label(
            text="",
            style=Pack(
                text_align = CENTER,
                font_weight = BOLD
            )
        )

        self.private_label = Label(
            text="Private",
            style=Pack(
                text_align = CENTER,
                color = GRAY,
                font_weight = BOLD
            )
        )

        self.private_value = Label(
            text="",
            style=Pack(
                text_align = CENTER,
                color = rgb(114,137,218),
                font_weight = BOLD
            )
        )
        self.unconfirmed_label = Label(
            text="Unconfirmed Balance",
            style=Pack(
                text_align = CENTER,
                color = GRAY,
                font_weight = BOLD,
                padding_top = 5
            )
        )
        self.unconfirmed_value = Label(
            text="",
            style=Pack(
                text_align = CENTER,
                color = RED,
                font_weight = BOLD,
                padding_bottom = 5
            )
        )
        self.unconfirmed_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = CENTER,
                padding_top = 70
            )
        )

        self.add(
            self.bitcoinz_logo,
            self.bitcoinz_title,
            self.balances_box
        )

        self.balances_box.add(
            self.total_balances_label,
            self.total_value,
            self.balances_type_box
        )

        self.balances_type_box.add(
            self.transparent_balance_box,
            self.private_balance_box
        )

        self.transparent_balance_box.add(
            self.transparent_label,
            self.transparent_value
        )
        self.private_balance_box.add(
            self.private_label,
            self.private_value
        )
        self.app.add_background_task(self.update_balances)


    async def update_balances(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            totalbalances,_ = await self.commands.z_getTotalBalance()
            if totalbalances is not None:
                balances = json.loads(totalbalances)
                totalbalance = self.units.format_balance(float(balances.get('total')))
                transparentbalance = self.units.format_balance(float(balances.get('transparent')))
                privatebalance = self.units.format_balance(float(balances.get('private')))
                self.total_value.text = totalbalance
                self.transparent_value.text = transparentbalance
                self.private_value.text = privatebalance
            unconfirmed_balance,_ = await self.commands.getUnconfirmedBalance()
            if unconfirmed_balance is not None:
                unconfirmed = self.units.format_balance(float(unconfirmed_balance))
                if float(unconfirmed) > 0:
                    if not self.unconfirmed_balance_toggle:
                        self.insert(2, self.unconfirmed_box)
                        self.unconfirmed_box.add(
                            self.unconfirmed_label,
                            self.unconfirmed_value
                        )
                        self.unconfirmed_balance_toggle = True
                    self.unconfirmed_value.text = unconfirmed
                else:
                    if self.unconfirmed_balance_toggle:
                        self.unconfirmed_box.remove(
                            self.unconfirmed_label,
                            self.unconfirmed_value
                        )
                        self.remove(self.unconfirmed_box)
                        self.unconfirmed_balance_toggle = False
                    
            await asyncio.sleep(5)

    
    def update_wallet_mode(self, widget):
        mode = self.utils.get_sys_mode()
        if mode:
            background_color = rgb(56,56,56)
        else:
            background_color = rgb(230,230,230)
        self.balances_box.style.background_color = background_color



class ImportKey(Window):
    def __init__(self, main:Window):
        super().__init__(
            size = (600, 150),
            resizable= False,
            closable=False
        )
        
        self.main = main
        self.utils = Utils(self.app)
        self.commands = Client(self.app)

        self.title = "Import Key"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )

        self.info_label = Label(
            text="Please enter your private key for transparent or private addresses.\n(This operation may take up to 10 minutes to complete.)",
            style=Pack(
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 11,
                padding_top = 5
            )
        )
        self.key_input = TextInput(
            style=Pack(
                text_align= CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 3,
                padding_left = 10
            )
        )
        
        self.import_button = Button(
            text="Import",
            style=Pack(
                alignment = CENTER,
                font_weight = BOLD,
                padding = (0,10,0,10)
            ),
            on_press=self.import_button_click
        )

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                alignment = CENTER,
                padding = (10,0,10,0)
            )
        )

        self.close_button = Button(
            text="Close",
            style=Pack(
                alignment = CENTER,
                font_weight = BOLD,
                padding_bottom = 10,
                width =100
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.input_box,
            self.close_button
        )
        self.input_box.add(
            self.key_input,
            self.import_button
        )

    def import_button_click(self, button):
        if not self.key_input.value:
            self.error_dialog(
                "Missing Private Key",
                "Please enter a private key to proceed."
            )
            self.key_input.focus()
            return
        self.main_position = self.main.position
        self.main.hide()
        self.key_input.readonly = True
        self.import_button.enabled = False
        self.close_button.enabled = False
        self.app.add_background_task(self.import_private_key)


    async def import_private_key(self, widget):
        key = self.key_input.value
        result, _= await self.commands.ImportPrivKey(key)
        if result is not None:
            pass
        else:
            result, _= await self.commands.z_ImportKey(key)
            if result is not None:
                pass
            else:
                self.main.position = self.main_position
                self.main.show()
                self.app.current_window = self
                self.error_dialog(
                    "Invalid Private Key",
                    "The private key you entered is not valid. Please check the format and try again."
                )
                self.update_import_window()
                return
        await self.import_key_status()


    async def import_key_status(self):
        while True:
            result,_ = await self.commands.getInfo()
            if result:
                self.main.position = self.main_position
                self.main.show()
                await self.main.update_wallet()
                return
            
            await asyncio.sleep(5)


    def update_import_window(self):
        self.key_input.readonly = False
        self.key_input.value = ""
        self.import_button.enabled = True
        self.close_button.enabled = True