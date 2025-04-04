
import asyncio
import json
import webbrowser

from toga import (
    App, Box, Label, ImageView, Window,
    Button, Table, TextInput
)
from ..framework import ClipBoard
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD, TOP
from toga.colors import rgb, GRAY, BLACK, YELLOW, TRANSPARENT

from .utils import Utils
from .units import Units
from .client import Client
from .storage import Storage



class ImportKey(Window):
    def __init__(self):
        super().__init__(
            size = (600, 150),
            resizable= False,
            closable=False
        )
        
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
                self.error_dialog(
                    "Invalid Private Key",
                    "The private key you entered is not valid. Please check the format and try again."
                )
        self.update_import_window()


    def update_import_window(self):
        self.key_input.readonly = False
        self.key_input.value = ""
        self.import_button.enabled = True
        self.close_button.enabled = True


class Recieve(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                padding = (2,5,0,5)
            )
        )

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.units = Units()
        self.storage = Storage(self.app)
        self.clipboard = ClipBoard()

        self.recieve_toggle = None
        self.transparent_toggle = None
        self.private_toggle = None

        mode = self.utils.get_sys_mode()
        if mode:
            copy_icon = "images/copy_w"
            key_icon = "images/key_w"
            explorer_icon = "images/explorer_w"
        else:
            copy_icon = "images/copy_b"
            key_icon = "images/key_b"
            explorer_icon = "images/explorer_b"

        self.addresses_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1
            )
        )

        self.addresses_list_box = Box(
            style=Pack(
                direction=COLUMN,
                flex = 1
            )
        )

        self.switch_address_box = Box(
            style=Pack(
                direction = ROW,
                alignment = TOP,
                height = 35
            )
        )

        self.transparent_button = Button(
            text="Transparent",
            style=Pack(
                flex = 1,
                font_weight = BOLD,
                color = GRAY
            ),
            on_press=self.transparent_button_click
        )
        
        self.private_button = Button(
            text="Private",
            style=Pack(
                flex = 1,
                font_weight = BOLD,
                color = GRAY
            ),
            on_press=self.private_button_click
        )

        self.addresses_list = Box(
            style=Pack(
                direction=COLUMN,
                flex = 1
            )
        )

        self.addresses_table = Table(
            headings=["Addresses"],
            accessors={"addresses"},
            style=Pack(
                flex = 1,
                font_weight = BOLD
            ),
            on_select=self.get_address_balance
        )

        self.address_info = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )
        self.address_qr = ImageView(
            style=Pack(
                background_color = GRAY,
                padding_top = 40,
                width = 217,
                height = 217,
                flex =1
            )
        )

        self.address_value = Label(
            text="",
            style=Pack(
                font_weight = BOLD,
                text_align = CENTER
            )
        )

        self.address_value_box = Box(
            style=Pack(
                direction = COLUMN,
                height=35,
                padding_top = 10
            )
        )

        self.address_balance = Label(
            text="",
            style=Pack(
                direction = COLUMN,
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 14,
                padding = (20,50,0,50),
                flex =1,
                alignment = TOP
            )
        )

        self.copy_address = Button(
            icon=copy_icon,
            on_press=self.copy_address_clipboard
        )
        self.copy_address._impl.native.set_tooltip_text("Copy the selected address")

        self.copy_key = Button(
            icon=key_icon,
            on_press=self.copy_key_clipboard
        )
        self.copy_key._impl.native.set_tooltip_text("Copy the key of selected address")

        self.explorer_address = Button(
            icon=explorer_icon,
            on_press=self.open_address_explorer
        )
        self.explorer_address._impl.native.set_tooltip_text("Open the selected in explorer")

        self.address_panel = Box(
            style=Pack(
                direction = ROW,
                flex = 1
            )
        )

        
    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.recieve_toggle:
            self.addresses_list.add(self.addresses_table)
            self.addresses_box.add(
                self.addresses_list_box,
                self.address_info
            )
            self.addresses_list_box.add(
                self.switch_address_box,
                self.addresses_list
            )
            self.switch_address_box.add(
                self.transparent_button,
                self.private_button
            )
            self.address_info.add(
                self.address_qr,
                self.address_value_box,
                self.address_balance,
                self.address_panel
            )
            self.address_value_box.add(
                self.address_value
            )
            self.address_panel.add(
                self.copy_address,
                self.copy_key,
                self.explorer_address
            )
            self.add(
                self.addresses_box
            )
            self.recieve_toggle = True
            self.transparent_button_click(None)
    

    def transparent_button_click(self, button):
        self.clear_buttons()
        self.transparent_toggle = True
        self.transparent_button.style.color = BLACK
        self.transparent_button.style.background_color = YELLOW
        self.app.add_background_task(self.display_transparent_addresses)

    async def display_transparent_addresses(self, widget):
        addresses = []
        transparent_addresses = await self.get_transparent_addresses()
        for address in transparent_addresses:
            row = {
                "addresses": address
            }
            addresses.append(row)
        self.addresses_table.data = addresses

    def private_button_click(self, button):
        self.clear_buttons()
        self.private_toggle = True
        self.private_button.style.color = BLACK
        self.private_button.style.background_color = rgb(114,137,218)
        self.app.add_background_task(self.display_private_addresses)


    async def display_private_addresses(self, widget):
        addresses = []
        private_addresses = await self.get_private_addresses()
        if private_addresses:
            for address in private_addresses:
                row = {
                    "addresses": address
                }
                addresses.append(row)
        else:
            addresses = [{
                "addresses": ""
            }]
        self.addresses_table.data = addresses

    def clear_buttons(self):
        if self.transparent_toggle:
            self.transparent_button.style.color = GRAY
            self.transparent_button.style.background_color = TRANSPARENT
            self.transparent_toggle = None

        elif self.private_toggle:
            self.private_button.style.color = GRAY
            self.private_button.style.background_color = TRANSPARENT
            self.private_toggle = None


    async def get_address_balance(self, table):
        if table.selection:
            row = table.selection
            balance, _ = await self.commands.z_getBalance(row.addresses)
            if balance is None:
                self.address_qr.image = None
                self.address_value.text = None
                return
            qr_image = self.utils.qr_generate(row.addresses)
            balance = self.units.format_balance(balance)
            self.address_qr.image = qr_image
            if len(row.addresses) > 38:
                first_part = row.addresses[:38]
                second_part = row.addresses[38:]
                self.address_value.text = f"{first_part}\n{second_part}"
            else:
                self.address_value.text = row.addresses
            self.address_balance.text = f"Balance : {balance}"


    def copy_address_clipboard(self, button):
        if not self.addresses_table.selection:
            return
        row = self.addresses_table.selection
        self.clipboard.copy(row.addresses)
        self.main.info_dialog(
            title="Copied",
            message="The address has been copied to clipboard.",
        )


    def open_address_explorer(self, button):
        if not self.addresses_table.selection:
            return
        url = "https://explorer.btcz.rocks/address/"
        row = self.addresses_table.selection
        transaction_url = url + row.addresses
        webbrowser.open(transaction_url)


    async def copy_key_clipboard(self, button):
        if not self.addresses_table.selection:
            return
        row = self.addresses_table.selection
        if self.transparent_toggle:
            result, _= await self.commands.DumpPrivKey(row.addresses)
        elif self.private_toggle:
            result, _= await self.commands.z_ExportKey(row.addresses)
        if result is not None:
            self.clipboard.copy(result)
            self.main.info_dialog(
                title="Copied",
                message="The private key has been copied to the clipboard.",
            )


    async def get_transparent_addresses(self):
        addresses_data,_ = await self.commands.ListAddresses()
        addresses_data = json.loads(addresses_data)
        if addresses_data is not None:
            address_items = {address_info for address_info in addresses_data}
        else:
            address_items = []
        return address_items
    

    async def get_private_addresses(self):
        addresses_data,_ = await self.commands.z_listAddresses()
        addresses_data = json.loads(addresses_data)
        if addresses_data:
            message_address = self.storage.get_identity("address")
            if message_address:
                address_items = {address_info for address_info in addresses_data if address_info != message_address[0]}
            else:
                address_items = {address_info for address_info in addresses_data}
        else:
            address_items = []
        return address_items
    

    def update_recieve_mode(self, widget):
        mode = self.utils.get_sys_mode()
        if mode:
            copy_icon = "images/copy_w"
            key_icon = "images/key_w"
            explorer_icon = "images/explorer_w"
        else:
            copy_icon = "images/copy_b"
            key_icon = "images/key_b"
            explorer_icon = "images/explorer_b"
        self.copy_address.icon = copy_icon
        self.copy_key.icon = key_icon
        self.explorer_address.icon = explorer_icon