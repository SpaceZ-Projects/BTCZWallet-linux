
import asyncio
import json
import webbrowser

from toga import (
    App, Box, Label, ImageView, Window,
    Button, Table
)
from ..framework import ClipBoard, Gtk, Gdk
from toga.style.pack import Pack
from toga.constants import COLUMN, ROW, CENTER, BOLD, TOP
from toga.colors import rgb, GRAY, BLACK, YELLOW, TRANSPARENT

from .utils import Utils
from .units import Units
from .client import Client
from .storage import Storage


class Receive(Box):
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
        self.units = Units(self.app)
        self.storage = Storage(self.app)
        self.clipboard = ClipBoard()

        self.recieve_toggle = None
        self.transparent_toggle = None
        self.private_toggle = None
        self.transparent_addresses_rows = []
        self.private_addresses_rows = []
        self.transparent_addresses = []
        self.private_addresses = []

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
        addresses_table_widgets = self.addresses_table._impl.native.get_child()
        addresses_table_widgets.connect("button-press-event", self.addresses_table_context_event)
        self.addresses_table_context_menu = Gtk.Menu()
        copy_address_item = Gtk.MenuItem(label="Copy address")
        copy_address_item.connect("activate", self.copy_address_clipboard)
        copy_key_item = Gtk.MenuItem(label="Copy private key")
        copy_key_item.connect("activate", self.copy_key_clipboard)
        explorer_address_item = Gtk.MenuItem(label="View address in explorer")
        explorer_address_item.connect("activate", self.open_address_explorer)
        self.addresses_table_context_menu.append(copy_address_item)
        self.addresses_table_context_menu.append(copy_key_item)
        self.addresses_table_context_menu.append(explorer_address_item)
        self.addresses_table_context_menu.show_all()

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
            
            self.add(
                self.addresses_box
            )
            self.recieve_toggle = True
            await self.transparent_button_click(None)


    def addresses_table_context_event(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.addresses_table_context_menu.popup_at_pointer(event)
            return True
        return False
    

    async def transparent_button_click(self, button):
        self.clear_buttons()
        self.transparent_toggle = True
        self.transparent_button.style.color = BLACK
        self.transparent_button.style.background_color = YELLOW
        self.transparent_addresses_rows.clear()
        self.transparent_addresses.clear()
        await self.display_transparent_addresses()

    async def display_transparent_addresses(self):
        transparent_addresses = await self.get_transparent_addresses()
        for address in transparent_addresses:
            row = {
                "addresses": address
            }
            self.transparent_addresses_rows.append(row)
            self.transparent_addresses.append(address)
        self.addresses_table.data = self.transparent_addresses_rows
        addresses_table_widgets = self.addresses_table._impl.native.get_child()
        selection = addresses_table_widgets.get_selection()
        path = Gtk.TreePath(0)
        selection.select_path(path)

    async def private_button_click(self, button):
        self.clear_buttons()
        self.private_toggle = True
        self.private_button.style.color = BLACK
        self.private_button.style.background_color = rgb(114,137,218)
        self.private_addresses_rows.clear()
        self.private_addresses.clear()
        await self.display_private_addresses()


    async def display_private_addresses(self):
        private_addresses = await self.get_private_addresses()
        if private_addresses:
            for address in private_addresses:
                row = {
                    "addresses": address
                }
                self.private_addresses_rows.append(row)
                self.private_addresses.append(address)
        else:
            self.private_addresses_rows = [{
                "addresses": ""
            }]
        self.addresses_table.data = self.private_addresses_rows
        addresses_table_widgets = self.addresses_table._impl.native.get_child()
        selection = addresses_table_widgets.get_selection()
        model = addresses_table_widgets.get_model()
        if model and len(model) > 0:
            path = Gtk.TreePath(0)
            selection.select_path(path)

    async def update_addresses(self):
        if self.recieve_toggle:
            if self.transparent_toggle:
                transparent_addresses = await self.get_transparent_addresses()
                if transparent_addresses:
                    for address in transparent_addresses:
                        if address not in self.transparent_addresses:
                            row = {
                                "addresses": address
                            }
                            self.transparent_addresses_rows.append(row)
                            self.transparent_addresses.append(address)
            elif self.private_toggle:
                private_addresses = await self.get_private_addresses()
                if private_addresses:
                    for address in private_addresses:
                        if address not in self.private_addresses:
                            row = {
                                "addresses": address
                            }
                            self.private_addresses_rows.append(row)
                            self.private_addresses.append(address)
            self.addresses_table.data.insert(0, row)


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


    def copy_address_clipboard(self, centext):
        if not self.addresses_table.selection:
            return
        row = self.addresses_table.selection
        self.clipboard.copy(row.addresses)
        self.main.info_dialog(
            title="Copied",
            message="The address has been copied to clipboard.",
        )


    def open_address_explorer(self, centext):
        if not self.addresses_table.selection:
            return
        url = "https://explorer.btcz.rocks/address/"
        row = self.addresses_table.selection
        transaction_url = url + row.addresses
        webbrowser.open(transaction_url)


    def copy_key_clipboard(self, centext):
        if not self.addresses_table.selection:
            return
        self.app.add_background_task(self.get_address_key)


    async def get_address_key(self, widget):
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