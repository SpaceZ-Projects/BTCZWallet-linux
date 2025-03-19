
import asyncio
import json

from toga import (
    App, Box, Label, TextInput, Selection, 
    ImageView, Window, Switch, MultilineTextInput,
    Button
)
from ..framework import Gtk, Gdk

from toga.style.pack import Pack
from toga.constants import (
    COLUMN, ROW, TOP, BOLD, CENTER, LEFT
)
from toga.colors import rgb, GRAY, YELLOW, BLACK, RED, TRANSPARENT
from .client import Client
from .utils import Utils
from .units import Units
from .storage import Storage


class Send(Box):
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

        self.send_toggle = None
        self.transparent_toggle = None
        self.private_toggle = None
        self.is_valid_toggle = None
        self.z_addresses_limit_toggle = None

        mode = self.utils.get_sys_mode()
        if mode:
            panel_color = rgb(56,56,56)
        else:
            panel_color = rgb(230,230,230)

        self.switch_box = Box(
            style=Pack(
                direction = ROW,
                alignment = TOP,
                height = 35,
                padding = (5,5,0,5)
            )
        )

        self.transparent_button = Button(
            text="Transparent",
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            ),
            on_press=self.transparent_button_click
        )

        self.private_button = Button(
            text="Private",
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 1
            ),
            on_press=self.private_button_click
        )

        self.from_address_label = Label(
            text="From :",
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                background_color = panel_color,
                font_size = 11,
                text_align = CENTER,
                padding = (16,0,0,10)
            )
        )
        self.address_selection = Selection(
            style=Pack(
                font_weight = BOLD,
                font_size = 11,
                flex = 2,
                padding = (10,10,0,10)
            ),
            accessor="select_address",
            on_change=self.display_address_balance
        )

        self.address_balance = Label(
            text="0.00000000",
            style=Pack(
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                text_align = CENTER,
                padding_right = 80
            )
        )

        self.selection_address_box = Box(
            style=Pack(
                direction = ROW,
                background_color = panel_color,
                padding=(10,5,0,5),
                height = 55
            )
        )

        self.single_option = Switch(
            text="Single",
            style=Pack(
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11
            ),
            on_change=self.single_option_on_change
        )
        self.single_option._impl.native.set_tooltip_text("Send to single address")

        self.many_option = Switch(
            text="Many",
            style=Pack(
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                padding_left = 20
            ),
            on_change=self.many_option_on_change
        )
        self.many_option._impl.native.set_tooltip_text("Send to many addresses")

        self.send_options_switch = Box(
            style=Pack(
                direction = ROW,
                background_color = panel_color,
                padding=(5,5,0,5),
                height = 35,
                alignment = CENTER
            )
        )
        self.send_options_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = panel_color,
                padding=(5,5,0,5),
                height = 35,
                alignment = CENTER
            )
        )

        self.destination_label = Label(
            text="To :",
            style=Pack(
                color = GRAY,
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                text_align = CENTER,
                flex = 1,
                padding_top = 16
            )
        )

        self.destination_input_single = TextInput(
            placeholder="address",
            style=Pack(
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                flex = 2,
                padding_top = 10
            ),
            on_change=self.is_valid_address
        )
        self.destination_input_single._impl.native.connect("button-press-event", self.destination_input_context_event)
        self.destination_input_context_menu = Gtk.Menu()
        send_to_message_item = Gtk.MenuItem(label="Send to messages address")
        send_to_message_item.connect("activate", self.set_destination_messages_address)
        self.destination_input_context_menu.append(send_to_message_item)
        self.destination_input_context_menu.show_all()

        self.destination_input_many = MultilineTextInput(
            placeholder="addresses list",
            style=Pack(
                font_weight = BOLD,
                font_size = 11,
                flex = 2,
                padding_top = 10,
                height = 75
            ),
            on_change=self.destination_input_many_on_change
        )

        self.is_valid = ImageView(
            style=Pack(
                background_color = panel_color,
                width = 30,
                height = 30,
                padding= (11,0,0,10)
            )
        )
        self.is_valid_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = panel_color,
                flex = 1 
            )
        )

        self.destination_box = Box(
            style=Pack(
                direction = ROW,
                background_color = panel_color,
                padding = (0,5,0,5),
                height = 55
            )
        )

        self.amount_label = Label(
            text="Amount :",
            style=Pack(
                color = GRAY,
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                text_align = CENTER,
                flex = 2,
                padding_top = 16
            )
        )

        self.amount_input = TextInput(
            placeholder="0.00000000",
            style=Pack(
                text_align= CENTER,
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                flex = 1,
                padding_top = 10
            ),
            validators=[
                self.is_digit
            ],
            on_change=self.verify_balance
        )
        self.amount_input._impl.native.connect("button-press-event", self.amount_input_context_event)
        self.amount_input_context_menu = Gtk.Menu()
        percentage_25_item = Gtk.MenuItem(label="%25 amount")
        percentage_25_item.connect("activate", self.set_25_amount)
        percentage_50_item = Gtk.MenuItem(label="%50 amount")
        percentage_50_item.connect("activate", self.set_50_amount)
        percentage_75_item = Gtk.MenuItem(label="%75 amount")
        percentage_75_item.connect("activate", self.set_75_amount)
        max_amount_item = Gtk.MenuItem(label="Max amount")
        max_amount_item.connect("activate", self.set_max_amount)
        self.amount_input_context_menu.append(percentage_25_item)
        self.amount_input_context_menu.append(percentage_50_item)
        self.amount_input_context_menu.append(percentage_75_item)
        self.amount_input_context_menu.append(max_amount_item)
        self.amount_input_context_menu.show_all()

        self.check_amount_label = Label(
            text="",
            style=Pack(
                color = RED,
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                text_align = LEFT,
                flex = 5,
                padding_top = 16,
                padding_left = 10
            )
        )

        self.split_option = Switch(
            text="Split",
            value=True,
            style=Pack(
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 10
            ),
            on_change=self.split_option_on_change
        )
        self.split_option._impl.native.set_tooltip_text("Split the total amount equally across all addresses")

        self.each_option = Switch(
            text="Each",
            style=Pack(
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 10,
                padding_left = 20
            ),
            on_change=self.each_option_on_change
        )
        self.each_option._impl.native.set_tooltip_text("Set a specific amount for each address")


        self.amount_options_switch = Box(
            style=Pack(
                direction = ROW,
                background_color = panel_color,
                height = 30,
                alignment = CENTER
            )
        )
        self.amount_options_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = panel_color,
                padding=(0,5,0,5),
                height = 30,
                alignment = CENTER
            )
        )

        self.amount_box = Box(
            style=Pack(
                direction = ROW,
                background_color = panel_color,
                padding = (5,5,0,5),
                height = 50
            )
        )

        self.fees_label = Label(
            text="Fee :",
            style=Pack(
                color = GRAY,
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                text_align = CENTER,
                flex = 2,
                padding_top = 16
            )
        )
        self.fee_input = TextInput(
            placeholder="0.00000000",
            style=Pack(
                text_align= CENTER,
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                flex = 1,
                padding_top = 10
            ),
            validators=[
                self.is_digit
            ]
        )
        self.fee_input._impl.native.connect("button-press-event", self.fee_input_context_event)
        self.fee_input_context_menu = Gtk.Menu()
        slow_item = Gtk.MenuItem(label="Slow")
        slow_item.connect("activate", self.set_slow_fee)
        normal_item = Gtk.MenuItem(label="Normal")
        normal_item.connect("activate", self.set_normal_fee)
        fast_item = Gtk.MenuItem(label="Fast")
        fast_item.connect("activate", self.set_fast_fee)
        self.fee_input_context_menu.append(slow_item)
        self.fee_input_context_menu.append(normal_item)
        self.fee_input_context_menu.append(fast_item)
        self.fee_input_context_menu.show_all()

        self.empty_box = Box(
            style=Pack(
                background_color = panel_color,
                flex = 5
            )
        )
        self.fees_box = Box(
           style=Pack(
                direction = ROW,
                background_color = panel_color,
                padding = (5,5,0,5),
                height = 50
            ) 
        )

        self.separator_box = Box(
           style=Pack(
                direction = ROW,
                flex = 1
            ) 
        )

        self.operation_label = Label(
            text="Operation Status :",
            style=Pack(
                color = GRAY,
                text_align= LEFT,
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11
            )
        )

        self.operation_status = Label(
            text="",
            style=Pack(
                text_align= LEFT,
                background_color = panel_color,
                font_weight = BOLD,
                font_size = 11,
                padding_left = 5
            )
        )

        self.operation_box = Box(
            style=Pack(
                direction = ROW,
                padding = (15,0,0,10)
            )
        )

        self.send_box = Box(
            style=Pack(
                direction = COLUMN,
                background_color = panel_color,
                flex = 1
            )
        )

        self.send_button = Button(
            text="Cash Out",
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                font_size = 12,
                width = 120,
                padding = (10,10,0,0)
            ),
            on_press = self.send_button_click
        )
        self.send_button._impl.native.connect("enter-notify-event", self.send_button_mouse_enter)
        self.send_button._impl.native.connect("leave-notify-event", self.send_button_mouse_leave)

        self.confirmation_box = Box(
            style=Pack(
                direction = ROW,
                background_color = panel_color,
                padding = 5,
                alignment = CENTER,
                height = 55
            )
        )


    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.send_toggle:
            self.add(
                self.switch_box,
                self.selection_address_box,
                self.send_options_box,
                self.destination_box,
                self.amount_box,
                self.separator_box,
                self.confirmation_box
            )
            self.switch_box.add(
                self.transparent_button,
                self.private_button
            )
            self.selection_address_box.add(
                self.from_address_label,
                self.address_selection
            )
            self.send_options_box.add(
                self.send_options_switch
            )
            self.send_options_switch.add(
                self.address_balance,
                self.single_option,
                self.many_option
            )
            self.destination_box.add(
                self.destination_label,
                self.is_valid_box
            )
            self.is_valid_box.add(
                self.is_valid
            )
            self.amount_box.add(
                self.amount_label,
                self.amount_input,
                self.check_amount_label
            )
            self.amount_options_switch.add(
                self.split_option,
                self.each_option
            )
            self.amount_options_box.add(
                self.amount_options_switch
            )
            self.fees_box.add(
                self.fees_label,
                self.fee_input,
                self.empty_box
            )
            self.confirmation_box.add(
                self.send_box,
                self.send_button
            )
            self.send_box.add(
                self.operation_box
            )
            self.operation_box.add(
                self.operation_label,
                self.operation_status
            )
            self.send_toggle = True
            self.transparent_button_click(None)


    def destination_input_context_event(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.destination_input_context_menu.popup_at_pointer(event)
            return True
        return False
    

    def amount_input_context_event(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.amount_input_context_menu.popup_at_pointer(event)
            return True
        return False
    
    def fee_input_context_event(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.fee_input_context_menu.popup_at_pointer(event)
            return True
        return False
    

    def set_destination_messages_address(self, context):
        selected_address = self.address_selection.value.select_address
        if selected_address == "Main Account":
            self.main.error_dialog(
                title="Error",
                message="You can't send amount from Main Account to messages (z) address."
            )
            return
        address = self.storage.get_identity("address")
        if address:
            value = address[0]
        else:
            value = "You don't have messages address yet !"
        self.destination_input_single.value = value


    def set_25_amount(self, context):
        if self.address_selection.value.select_address:
            selected_address = self.address_selection.value.select_address
            balance = self.address_balance.text
            if selected_address == "Main Account":
                if float(balance) > 0.0002:
                    balance_after_fee = float(balance) - 0.0001
                    amount = balance_after_fee * 0.25
                    self.amount_input.value = f"{amount:.8f}"
            else:
                if float(balance) > 0:
                    fee = self.fee_input.value
                    balance_after_fee = float(balance) - float(fee)
                    amount = balance_after_fee * 0.25
                    self.amount_input.value = f"{amount:.8f}"


    def set_50_amount(self, context):
        if self.address_selection.value.select_address:
            selected_address = self.address_selection.value.select_address
            balance = self.address_balance.text
            if selected_address == "Main Account":
                if float(balance) > 0.0002:
                    balance_after_fee = float(balance) - 0.0001
                    amount = balance_after_fee * 0.50
                    self.amount_input.value = f"{amount:.8f}"
            else:
                if float(balance) > 0:
                    fee = self.fee_input.value
                    balance_after_fee = float(balance) - float(fee)
                    amount = balance_after_fee * 0.50
                    self.amount_input.value = f"{amount:.8f}"


    def set_75_amount(self, context):
        if self.address_selection.value.select_address:
            selected_address = self.address_selection.value.select_address
            balance = self.address_balance.text
            if selected_address == "Main Account":
                if float(balance) > 0.0002:
                    balance_after_fee = float(balance) - 0.0001
                    amount = balance_after_fee * 0.75
                    self.amount_input.value = f"{amount:.8f}"
            else:
                if float(balance) > 0:
                    fee = self.fee_input.value
                    balance_after_fee = float(balance) - float(fee)
                    amount = balance_after_fee * 0.75
                    self.amount_input.value = f"{amount:.8f}"


    def set_max_amount(self, context):
        if self.address_selection.value.select_address:
            selected_address = self.address_selection.value.select_address
            balance = self.address_balance.text
            if selected_address == "Main Account":
                if float(balance) > 0.0002:
                    amount = float(balance) - 0.0001
                    self.amount_input.value = f"{amount:.8f}"
            else:
                if float(balance) > 0:
                    fee = self.fee_input.value
                    amount = float(balance) - float(fee)
                    self.amount_input.value = f"{amount:.8f}"


    def set_slow_fee(self, context):
        self.fee_input.value = "0.00000100"

    def set_normal_fee(self, context):
        self.fee_input.value = "0.00001000"

    def set_fast_fee(self, context):
        self.fee_input.value = "0.00010000"


    def transparent_button_click(self, button):
        self.clear_buttons()
        self.transparent_toggle = True
        self.transparent_button.style.color = BLACK
        self.transparent_button.style.background_color = YELLOW
        self.address_selection.focus()
        self.app.add_background_task(self.update_send_options)

    
    def private_button_click(self, button):
        self.clear_buttons()
        self.private_toggle = True
        self.private_button.style.color = BLACK
        self.private_button.style.background_color = rgb(114,137,218)
        self.address_selection.focus()
        self.app.add_background_task(self.update_send_options)


    async def update_send_options(self, widegt):
        if self.transparent_toggle:
            selection_items = await self.get_transparent_addresses()
        if self.private_toggle:
            selection_items = await self.get_private_addresses()

        self.address_selection.items.clear()
        self.address_selection.items = selection_items

    def clear_buttons(self):
        if self.transparent_toggle:
            self.transparent_button.style.color = GRAY
            self.transparent_button.style.background_color = TRANSPARENT
            self.transparent_toggle = None

        elif self.private_toggle:
            self.private_button.style.color = GRAY
            self.private_button.style.background_color = TRANSPARENT
            self.private_toggle = None


    async def get_transparent_addresses(self):
        addresses_data, _ = await self.commands.ListAddresses()
        if addresses_data:
            addresses_data = json.loads(addresses_data)
        else:
            addresses_data = []
        if addresses_data is not None:
            address_items = [("Main Account")] + [(address_info, address_info) for address_info in addresses_data]
        else:
            address_items = [("Main Account")]
        return address_items
    
    
    async def get_private_addresses(self):
        addresses_data, _ = await self.commands.z_listAddresses()
        addresses_data = json.loads(addresses_data)
        if addresses_data:
            message_address = self.storage.get_identity("address")
            if message_address:
                address_items = [address_info for address_info in addresses_data if address_info != message_address[0]]
            else:
                address_items = [address_info for address_info in addresses_data]
        else:
            address_items = []
        return address_items
    
    
    async def display_address_balance(self, selection):
        if selection.value is None:
            self.address_balance.text = "0.00000000"
            return
        self.amount_input.value = ""
        selected_address = selection.value.select_address
        if selected_address != "Main Account":
            self.single_option.enabled = True
            self.many_option.enabled =True
            if self.many_option.value is False:
                self.update_fees_option(True)
            balance, _ = await self.commands.z_getBalance(selected_address)
            if balance:
                format_balance = self.units.format_balance(float(balance))
                self.address_balance.text = format_balance

        elif selected_address == "Main Account":
            self.single_option.value = True
            self.single_option.enabled = False
            self.many_option.enabled =False
            self.update_fees_option(False)
            total_balances, _ = await self.commands.z_getTotalBalance()
            if total_balances:
                balances = json.loads(total_balances)
                transparent = balances.get('transparent')
                format_balance = self.units.format_balance(float(transparent))
                self.address_balance.text = format_balance
        else:
            self.address_balance.text = "0.00000000"


    def single_option_on_change(self, switch):
        if switch.value is True:
            self.many_option.value = False
            self.destination_box.insert(1, self.destination_input_single)
            self.destination_input_single.readonly = False
            self.update_fees_option(True)
            self.is_valid_toggle = None
        else:
            if self.many_option.value is True:
                self.single_option.value = False
                self.destination_box.remove(
                    self.destination_input_single
                )
            else:
                self.single_option.value = True
        
    def many_option_on_change(self, switch):
        if switch.value is True:
            self.single_option.value = False
            self.destination_box.style.height = 100
            self.destination_box.insert(1, self.destination_input_many)
            self.insert(5, self.amount_options_box)
            self.update_fees_option(False)
            self.is_valid_toggle = True
        else:
            if self.single_option.value is True:
                self.many_option.value = False
                self.destination_box.style.height = 55
                self.destination_box.remove(
                    self.destination_input_many
                )
                self.remove(self.amount_options_box)
            else:
                self.many_option.value = True


    def split_option_on_change(self, switch):
        if switch.value is True:
            self.each_option.value = False
        else:
            if self.each_option.value is True:
                self.split_option.value = False
            else:
                self.split_option.value = True

    def each_option_on_change(self, switch):
        if switch.value is True:
            self.split_option.value = False
        else:
            if self.split_option.value is True:
                self.each_option.value = False
            else:
                self.each_option.value = True


    async def clear_inputs(self):
        if self.transparent_toggle:
            selection_items = await self.get_transparent_addresses()
        if self.private_toggle:
            selection_items = await self.get_private_addresses()
        self.address_selection.items.clear()
        self.address_selection.items = selection_items
        if self.many_option.value is True:
            self.destination_input_many.value = ""
        elif self.single_option.value is True:
            self.destination_input_single.value = ""
        self.amount_input.value = ""

    def update_fees_option(self, option):
        if option:
            self.insert(5, self.fees_box)
            self.app.add_background_task(self.set_default_fee)
        else:
            self.remove(self.fees_box)

    async def set_default_fee(self, widget):
        result, _= await self.commands.getInfo()
        result = json.loads(result)
        if result is not None:
            paytxfee = result.get('paytxfee')
            relayfee = result.get('relayfee')
        if paytxfee == 0.0:
            self.fee_input.value = f"{relayfee:.8f}"
        else:
            self.fee_input.value = f"{paytxfee:.8f}"


    async def is_valid_address(self, input):
        address = self.destination_input_single.value
        if not address:
            self.is_valid.image = None
            return
        if address.startswith("t"):
            result, _ = await self.commands.validateAddress(address)
        elif address.startswith("z"):
            result, _ = await self.commands.z_validateAddress(address)
        else:
            self.is_valid.image = "images/notvalid.png"
            return
        if result is not None:
            result = json.loads(result)
            is_valid = result.get('isvalid')
            if is_valid is True:
                self.is_valid.image = "images/valid.png"
                self.is_valid_toggle = True
            elif is_valid is False:
                self.is_valid.image = "images/notvalid.png"
                self.is_valid_toggle = False


    async def destination_input_many_on_change(self, input):
        addresses = self.destination_input_many.value
        if not addresses:
            self.is_valid.image = None
            return
        inputs_lines = addresses.strip().split('\n')
        count_z_addresses = sum(1 for address in inputs_lines if address.strip().lower().startswith('z'))
        if count_z_addresses > 54:
            self.z_addresses_limit_toggle = True
            return
        self.z_addresses_limit_toggle = False


    
    async def verify_balance(self, input):
        amount = self.amount_input.value
        if not amount:
            self.check_amount_label.text = ""
            return
        balance = self.address_balance.text
        if float(balance) < float(amount):
            self.check_amount_label.text = "Insufficient"
        else:
            self.check_amount_label.text = ""


    def is_digit(self, value):
        if not self.amount_input.value.replace('.', '', 1).isdigit():
            self.amount_input.value = ""
        if not self.fee_input.value.replace('.', '', 1).isdigit():
            self.fee_input.value = ""


    def send_button_click(self, button):
        selected_address = self.address_selection.value.select_address if self.address_selection.value else None
        if self.many_option.value is True:
            destination_address = self.destination_input_many.value
        else:
            destination_address = self.destination_input_single.value
        amount = self.amount_input.value
        balance = self.address_balance.text
        if selected_address is None:
            self.main.error_dialog(
                "Oops! No address selected",
                "Please select the address you want to send from."
            )
            self.address_selection.focus()
            return
        elif destination_address == "":
            self.main.error_dialog(
                "Destination address is missing",
                "Please enter a destination address where you want to send the funds."
            )
            if self.many_option.value is True:
                self.destination_input_many.focus()
            else:
                self.destination_input_single.focus()
            return
        elif self.z_addresses_limit_toggle:
            self.main.error_dialog(
                title="Error",
                message="The maximum number of zaddr outputs is 54 due to transaction size limits."
            )
            return
        elif not self.is_valid_toggle:
            self.main.error_dialog(
                "Error",
                "The destination address is not valid"
            )
            self.destination_input_single.focus()
            return
        elif amount == "":
            self.main.error_dialog(
                "Amount not entered",
                "Please specify the amount you wish to send."
            )
            self.amount_input.focus()
            return
        elif float(balance) < float(amount):
            self.main.error_dialog(
                "Insufficient balance",
                "You don't have enough balance to complete this transaction. Please adjust the amount."
            )
            self.amount_input.focus()
            return
        self.app.add_background_task(self.make_transaction)


    async def make_transaction(self, widget):
        self.disable_send()
        selected_address = self.address_selection.value.select_address
        amount = self.amount_input.value
        txfee = self.fee_input.value
        balance = self.address_balance.text
        if self.many_option.value is True:
            destination_address = self.destination_input_many.value
            addresses_array = self.create_addresses_array(destination_address)
            await self.send_many(selected_address, addresses_array)
        else:
            destination_address = self.destination_input_single.value
            await self.send_single(selected_address, destination_address, amount, txfee, balance)


    async def send_single(self, selected_address, destination_address, amount, txfee, balance):
        try:
            if selected_address == "Main Account" and destination_address.startswith("t"):
                operation, _= await self.commands.sendToAddress(destination_address, amount)
                if operation is not None:
                    self.main.info_dialog(
                        title="Success",
                        message="Transaction success"
                    )
                    await self.clear_inputs()
                else:
                    self.main.error_dialog(
                        title="Error",
                        message="Transaction failed."
                    )
                self.enable_send()
            elif selected_address != "Main Account":
                if (float(amount)+float(txfee)) > float(balance):
                    self.main.error_dialog(
                        "Insufficient balance",
                        "You don't have enough balance to complete this transaction. Please adjust the amount."
                    )
                    self.enable_send()
                    return
                operation, _= await self.commands.z_sendMany(selected_address, destination_address, amount, txfee)
                if operation:
                    transaction_status, _= await self.commands.z_getOperationStatus(operation)
                    transaction_status = json.loads(transaction_status)
                    if isinstance(transaction_status, list) and transaction_status:
                        status = transaction_status[0].get('status')
                        self.operation_status.text = status
                        if status == "executing" or status =="success":
                            await asyncio.sleep(1)
                            while True:
                                transaction_result, _= await self.commands.z_getOperationResult(operation)
                                transaction_result = json.loads(transaction_result)
                                if isinstance(transaction_result, list) and transaction_result:
                                    status = transaction_result[0].get('status')
                                    self.operation_status.text = status
                                    if status == "failed":
                                        self.enable_send()
                                        self.main.error_dialog(
                                            title="Error",
                                            message="Transaction failed."
                                        )
                                        return
                                    self.enable_send()
                                    self.main.info_dialog(
                                        title="Success",
                                        message="Transaction success"
                                    )
                                    await self.clear_inputs()
                                    return
                                await asyncio.sleep(3)
                else:
                    self.enable_send()
                    self.main.error_dialog(
                        title="Error",
                        message="Transaction failed."
                    )
        except Exception as e:
            self.enable_send()
            print(f"An error occurred: {e}")



    def create_addresses_array(self, addresses_list):
        addresses = [line.strip() for line in addresses_list.strip().split('\n') if line.strip()]
        amount_value = self.amount_input.value
        if self.split_option.value is True:
            amount = float(amount_value) / len(addresses)
            amount = f"{amount:.8f}"
        elif self.each_option.value is True:
            total_amount = float(amount_value) * len(addresses)
            address_balance = self.address_balance.text
            if float(total_amount) > float(address_balance):
                self.main.error_dialog(
                    "Error...",
                    f"Insufficient balance for this transaction.\nTotal amount = {total_amount:.8f}"
                )
                return
            else:
                amount = amount_value
        transactions = [{"address": address, "amount": amount} for address in addresses]
        return transactions


    
    async def send_many(self, selected_address, destination_address):
        try:
            operation, _= await self.commands.z_sendToManyAddresses(selected_address, destination_address)
            if operation:
                transaction_status, _= await self.commands.z_getOperationStatus(operation)
                transaction_status = json.loads(transaction_status)
                if isinstance(transaction_status, list) and transaction_status:
                    status = transaction_status[0].get('status')
                    self.operation_status.text = status
                    if status == "executing" or status =="success":
                        await asyncio.sleep(1)
                        while True:
                            transaction_result, _= await self.commands.z_getOperationResult(operation)
                            transaction_result = json.loads(transaction_result)
                            if isinstance(transaction_result, list) and transaction_result:
                                status = transaction_status[0].get('status')
                                self.operation_status.text = status
                                if status == "failed":
                                    self.enable_send()
                                    self.main.error_dialog(
                                        title="Error",
                                        message="Transaction failed."
                                    )
                                    return
                                self.enable_send()
                                self.main.info_dialog(
                                    title="Success",
                                    message="Transaction success"
                                )
                                await self.clear_inputs()
                                return
                            await asyncio.sleep(3)
            else:
                self.enable_send()
                self.main.error_dialog(
                    title="Error",
                    message="Transaction failed."
                )
        except Exception as e:
            self.enable_send()
            print(f"An error occurred: {e}")

    
    def disable_send(self):
        self.send_button.enabled = False
        if self.many_option.value is True:
            self.destination_input_many.readonly = True
        elif self.single_option.value is True:
            self.destination_input_single.readonly = True
        self.amount_input.readonly = True
        self.fee_input.readonly = True


    def enable_send(self):
        self.send_button.enabled = True
        if self.many_option.value is True:
            self.destination_input_many.readonly = False
        elif self.single_option.value is True:
            self.destination_input_single.readonly = False
        self.amount_input.readonly = False
        self.fee_input.readonly = False
        self.operation_status.text = ""

    
    def send_button_mouse_enter(self, widget, event):
        self.send_button.style.color = BLACK
        if self.transparent_toggle:
            self.send_button.style.background_color = YELLOW
        elif self.private_toggle:
            self.send_button.style.background_color = rgb(114,137,218)

    def send_button_mouse_leave(self, widget, event):
        self.send_button.style.color = GRAY
        self.send_button.style.background_color = TRANSPARENT


    def update_send_mode(self, widegt):
        mode = self.utils.get_sys_mode()
        if mode:
            panel_color = rgb(56,56,56)
        else:
            panel_color = rgb(230,230,230)
        self.from_address_label.style.background_color = panel_color
        self.address_balance.style.background_color = panel_color
        self.selection_address_box.style.background_color = panel_color
        self.single_option.style.background_color = panel_color
        self.many_option.style.background_color = panel_color
        self.send_options_switch.style.background_color = panel_color
        self.send_options_box.style.background_color = panel_color
        self.destination_label.style.background_color = panel_color
        self.destination_input_single.style.background_color = panel_color
        self.is_valid.style.background_color = panel_color
        self.is_valid_box.style.background_color = panel_color
        self.destination_box.style.background_color = panel_color
        self.amount_label.style.background_color = panel_color
        self.amount_input.style.background_color = panel_color
        self.check_amount_label.style.background_color = panel_color
        self.split_option.style.background_color = panel_color
        self.each_option.style.background_color = panel_color
        self.amount_options_switch.style.background_color = panel_color
        self.amount_options_box.style.background_color = panel_color
        self.amount_box.style.background_color = panel_color
        self.fees_label.style.background_color = panel_color
        self.fee_input.style.background_color = panel_color
        self.empty_box.style.background_color = panel_color
        self.fees_box.style.background_color = panel_color
        self.operation_label.style.background_color = panel_color
        self.operation_status.style.background_color = panel_color
        self.send_box.style.background_color = panel_color
        self.confirmation_box.style.background_color = panel_color
