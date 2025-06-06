
import asyncio
import json
import binascii
from datetime import datetime
from decimal import Decimal
from functools import partial

from toga import (
    App, Box, Window, Button, Label, TextInput,
    ScrollContainer, ImageView, MultilineTextInput
)
from ..framework import ClipBoard, Gtk, Gdk, is_wsl, Menu, Command
from toga.style.pack import Pack
from toga.constants import ROW, CENTER, COLUMN, BOLD, BOTTOM
from toga.colors import (
    rgb, BLACK, GRAY, RED, ORANGE, TRANSPARENT, GREENYELLOW, WHITE
)

from .storage import Storage
from .utils import Utils
from .units import Units
from .client import Client
from .settings import Settings

if not is_wsl():
    from ..framework import NotifyGtk



class EditUser(Window):
    def __init__(self, username, main:Window):
        super().__init__(
            size = (500, 150),
            resizable= False,
            closable=False
        )

        self.utils = Utils(self.app)
        self.storage = Storage(self.app)
        self.username = username
        self.main = main

        self.title = "Edit Username"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self._impl.native.set_keep_above(True)
        self._impl.native.set_modal(True)

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )
        self.info_label = Label(
            text="Edit your messages username",
            style=Pack(
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 12,
                padding_top = 5
            )
        )
        self.username_label = Label(
            text="Username :",
            style=Pack(
                color = GRAY,
                font_size = 12,
                font_weight = BOLD,
                padding= (5,5,0,0)
            )
        )
        self.username_input = TextInput(
            value=self.username,
            placeholder="required",
            style=Pack(
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                width = 250
            )
        )
        self.username_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                padding_top = 15
            )
        )

        self.change_button = Button(
            text="Change",
            style=Pack(
                color = GRAY,
                font_size=12,
                font_weight = BOLD,
                alignment = CENTER,
                padding_bottom = 10,
                padding_left = 15
            ),
            on_press=self.verify_username
        )
        self.change_button._impl.native.connect("enter-notify-event", self.change_button_mouse_enter)
        self.change_button._impl.native.connect("leave-notify-event", self.change_button_mouse_leave)

        self.cancel_button = Button(
            text="Cancel",
            style=Pack(
                color = GRAY,
                font_size=12,
                font_weight = BOLD,
                alignment = CENTER,
                padding_bottom = 10
            ),
            on_press=self.close_edit_username
        )
        self.cancel_button._impl.native.connect("enter-notify-event", self.cancel_button_mouse_enter)
        self.cancel_button._impl.native.connect("leave-notify-event", self.cancel_button_mouse_leave)

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER
            )
        )
        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.username_box,
            self.buttons_box
        )
        self.username_box.add(
            self.username_label,
            self.username_input,
            self.change_button
        )
        self.buttons_box.add(
            self.cancel_button
        )

    async def verify_username(self, button):
        def on_result(widget, result):
            if result is None:
                self.close()
        if not self.username_input.value:
            self.error_dialog(
                title="Missing Username",
                message="The username is required for messages address."
            )
            return
        if self.username_input.value == self.username:
            self.error_dialog(
                title="Duplicate Username",
                message="The username you entered is the same as your current username."
            )
            return
        username = self.username_input.value
        self.storage.edit_username(self.username, username)
        self.info_dialog(
            title="Updated Successfully",
            message="Your username has been successfully updated.",
            on_result=on_result
        )


    def change_button_mouse_enter(self, widget, event):
        self.change_button.style.color = BLACK
        self.change_button.style.background_color = GREENYELLOW

    def change_button_mouse_leave(self, widget, event):
        self.change_button.style.color = GRAY
        self.change_button.style.background_color = TRANSPARENT


    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = WHITE
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = GRAY
        self.cancel_button.style.background_color = TRANSPARENT
    

    def close_edit_username(self, button):
        self.close()



class Indentifier(Window):
    def __init__(self, messages_page:Box, main:Window, chat:Box):
        super().__init__(
            size = (650, 150),
            resizable= False,
            closable=False
        )

        self.messages_page = messages_page
        self.main = main
        self.chat = chat

        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.storage = Storage(self.app)

        self.title = "Setup Indentity"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self._impl.native.set_keep_above(True)
        self._impl.native.set_modal(True)

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )
        self.info_label = Label(
            text="For fist time a username is required for address indentity, you can edit it later",
            style=Pack(
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 11,
                padding_top = 5
            )
        )
        self.username_label = Label(
            text="Username :",
            style=Pack(
                color = GRAY,
                font_size = 12,
                font_weight = BOLD,
                padding = (5,10,0,0)
            )
        )
        self.username_input = TextInput(
            placeholder="required",
            style=Pack(
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                width = 250
            )
        )
        self.username_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                padding_top = 15
            )
        )

        self.cancel_button = Button(
            text="Cancel",
            style=Pack(
                color=GRAY,
                font_weight = BOLD,
                font_size = 12,
                alignment = CENTER,
                padding_bottom = 10,
                padding_right = 10
            ),
            on_press=self.close_identity_setup
        )
        self.cancel_button._impl.native.connect("enter-notify-event", self.cancel_button_mouse_enter)
        self.cancel_button._impl.native.connect("leave-notify-event", self.cancel_button_mouse_leave)

        self.create_button = Button(
            text="Create",
            style=Pack(
                color=GRAY,
                font_weight = BOLD,
                font_size = 12,
                alignment = CENTER,
                padding_bottom = 10,
                padding_left = 10
            ),
            on_press=self.verify_identity
        )
        self.create_button._impl.native.connect("enter-notify-event", self.create_button_mouse_enter)
        self.create_button._impl.native.connect("leave-notify-event", self.create_button_mouse_leave)

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.username_box,
            self.buttons_box
        )
        self.username_box.add(
            self.username_label,
            self.username_input
        )
        self.buttons_box.add(
            self.cancel_button,
            self.create_button
        )

    async def verify_identity(self, button):
        if not self.username_input.value:
            self.error_dialog(
                title="Missing Username",
                message="The username is required for messages address"
            )
            self.username_input.focus()
            return
        await self.setup_new_identity()


    async def setup_new_identity(self):
        def on_result(widget, result):
            if result is None:
                self.close()
                self.messages_page.clear()
                self.messages_page.add(self.chat)
                self.chat.run_tasks()
        category = "individual"
        username = self.username_input.value
        messages_address, _ = await self.commands.z_getNewAddress()
        if messages_address:
            prv_key, _= await self.commands.z_ExportKey(messages_address)
            if prv_key:
                self.storage.key(prv_key)
            self.storage.identity(category, username, messages_address)
            
            self.main.info_dialog(
                title="Identity Setup Complete!",
                message=f"Success! Your new identity has been securely set up with the username:\n\n"
                        f"Username: {username}\nAddress: {messages_address}\n\n"
                        "Your messages address and private key have been stored.",
                on_result=on_result
            )


    def create_button_mouse_enter(self, widget, event):
        self.create_button.style.color = BLACK
        self.create_button.style.background_color = GREENYELLOW

    def create_button_mouse_leave(self, widget, event):
        self.create_button.style.color = GRAY
        self.create_button.style.background_color = TRANSPARENT


    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = WHITE
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = GRAY
        self.cancel_button.style.background_color = TRANSPARENT

    
    def close_identity_setup(self, button):
        self.close()


class NewMessenger(Box):
    def __init__(self, messages_page:Box, main:Window, chat:Box):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )

        self.messages_page = messages_page
        self.main = main
        self.chat = chat

        self.new_identity_toggel = None

        self.new_label = Label(
            text="There no messages address for this wallet, click the button to create new messages address",
            style=Pack(
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 11
            )
        )

        self.create_button = Button(
            text="New Messenger",
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                font_size = 12,
                width = 160,
                padding_top = 7
            ),
            on_press=self.create_button_click
        )
        self.create_button._impl.native.connect("enter-notify-event", self.create_button_mouse_enter)
        self.create_button._impl.native.connect("leave-notify-event", self.create_button_mouse_leave)

        self.add(
            self.new_label,
            self.create_button
        )


    def create_button_click(self, button):
        self.indentity = Indentifier(self.messages_page, self.main, self.chat)
        self.indentity.show()


    def create_button_mouse_enter(self, widget, event):
        self.create_button.style.color = BLACK
        self.create_button.style.background_color = rgb(114,137,218)

    def create_button_mouse_leave(self, widget, event):
        self.create_button.style.color = GRAY
        self.create_button.style.background_color = TRANSPARENT


    def close_indentity_setup(self, button):
        self.indentity.close()
        self.new_identity_toggel = None



class Message(Box):
    def __init__(self, author, message, amount, timestamp, app:App, output:ScrollContainer):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                padding = (0,0,5,0),
            )
        )

        self.app = app
        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.output_box = output
        
        self.author = author
        self.message = message
        self.amount = amount
        self.timestamp = timestamp

        self.wheel = 0

        if self.author == "you":
            color = GRAY
        else:
            color = rgb(114,137,218)

        message_time = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

        self.author_value = Label(
            text=f"{self.author} :",
            style=Pack(
                color = color,
                font_size = 11,
                font_weight = BOLD,
                padding = (5,0,8,5),
                flex = 1
            )
        )

        self.gift_value = Label(
            text="",
            style=Pack(
                font_weight = BOLD,
                padding = (5,5,0,0)
            )
        )

        self.message_time = Label(
            text=message_time,
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                padding = (8,5,0,0)
            )
        )

        self.sender_box = Box(
            style=Pack(
                direction = ROW,
                padding_bottom = 5
            )
        )

        self.message_value = MultilineTextInput(
            value=f"{self.message}",
            readonly=True,
            style=Pack(
                font_weight = BOLD,
                flex = 1
            )
        )
        self.message_value._impl.native.connect("scroll-event", self.on_scroll)
        message_value = self.message_value._impl.native.get_child()
        message_value.set_left_margin(5)

        self.message_box = Box(
            style=Pack(
                direction = ROW,
                padding_left = 10 
            )
        )
        self.add(
            self.sender_box,
            self.message_box
        )
        if self.amount > 0.0001:
            gift = self.amount - 0.0001
            gift_format = self.units.format_balance(gift)
            self.gift_value.text = f"Gift : {gift_format}"
            self.sender_box.add(
                self.author_value,
                self.gift_value,
                self.message_time
            )
        else:
            self.sender_box.add(
                self.author_value,
                self.message_time
            )
        self.message_box.add(self.message_value)


    def on_scroll(self, widget, event):
        if event.delta_y > 0:
            self.wheel = 20
        elif event.delta_y < 0:
            self.wheel = -20
        postion = self.output_box.vertical_position + self.wheel
        self.output_box.vertical_position = postion



class Contact(Box):
    def __init__(self, category, contact_id, username, address, app:App, chat, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                padding = (5,5,0,5),
                height = 50
            )
        )

        self.app =app
        self.chat = chat
        self.main = main
        self.utils = Utils(self.app)
        self.storage = Storage(self.app)
        self.clipboard = ClipBoard()

        self.category = category
        self.contact_id = contact_id
        self.username = username
        self.address = address
        
        if self.utils.get_sys_mode():
            if self.category == "individual":
                image_path = "images/individual_w.png"
            elif self.category == "group":
                image_path = "images/group_w.png"
        else:
            if self.category == "individual":
                image_path = "images/individual_b.png"
            elif self.category == "group":
                image_path = "images/group_b.png"

        self.category_icon = Button(
            icon=image_path,
            style=Pack(
                padding_left = 5
            )
        )

        self.username_label = Button(
            text=self.username,
            style=Pack(
                flex = 1,
                font_size = 11,
                font_weight = BOLD,
                padding = (6,0,0,1)
            )
        )

        self.unread_messages = Label(
            text="",
            style=Pack(
                text_align = CENTER,
                font_size = 9,
                font_weight = BOLD,
                padding =(15,10,0,10)
            )
        )

        self.add(
            self.category_icon,
            self.username_label,
            self.unread_messages
        )

        self.username_label._impl.native.connect("button-press-event", self.contact_context_event)
        self.contact_context_menu = Menu()
        self.copy_address_cmd = Command(
            title="Copy address",
            action=self.copy_address
        )
        self.ban_address_cmd = Command(
            title="Ban contact",
            action=self.ban_address
        )
        self.contact_context_menu.add_commands(
            [
                self.copy_address_cmd,
                self.ban_address_cmd
            ]
        )
        self.set_contact_context_icons()
        self.app.add_background_task(self.update_contact)


    def set_contact_context_icons(self):
        if self.utils.get_sys_mode():
            self.copy_address_cmd.icon = "images/copy_w.png"
        else:
            self.copy_address_cmd.icon = "images/copy_b.png"


    def contact_context_event(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.contact_context_menu.popup_at_pointer(event)
            return True
        return False
    

    def copy_address(self, centext):
        self.clipboard.copy(self.address)
        self.main.info_dialog(
            title="Copied",
            message="The address has copied to clipboard.",
        )


    def ban_address(self, context):
        def on_result(widget, result):
            def on_second_result(widget, result):
                if result is None:
                    if self.chat.selected_contact_toggle:
                        self.chat.contact_info_box.clear()
                        self.chat.messages_box.clear()
                        self.chat.last_message_timestamp = None
                        self.chat.last_unread_timestamp = None
                        self.chat.selected_contact_toggle = None
            if result is True:
                self.storage.ban(self.address)
                self.storage.delete_contact(self.address)
                self.chat.contacts_box.remove(self)
                self.main.info_dialog(
                    title="Contact Banned",
                    message=f"The contact has been successfully banned and deleted:\n\n"
                            f"- Username: {self.username}\n"
                            f"- User ID: {self.contact_id}\n"
                            f"- Address: {self.address}",
                    on_result=on_second_result
                )

        self.main.question_dialog(
            title="Ban Contact",
            message=f"Are you sure you want to ban and delete this contact?\n\n"
                    f"- Username: {self.username}\n"
                    f"- User ID: {self.contact_id}\n"
                    f"- Address: {self.address}",
            on_result=on_result
        )


    async def update_contact(self, widget):
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue
            username = self.storage.get_contact_username(self.contact_id)
            if username:
                self.username_label.text = username[0]
            unread_messages = self.storage.get_unread_messages(self.contact_id)
            if unread_messages:
                unread_count = len(unread_messages)
                self.unread_messages.text = unread_count
            else:
                self.unread_messages.text = ""
            await asyncio.sleep(3)


    def update_contact_mode(self, wdiget):
        if self.utils.get_sys_mode():
            if self.category == "individual":
                image_path = "images/individual_w.png"
            elif self.category == "group":
                image_path = "images/group_w.png"
        else:
            if self.category == "individual":
                image_path = "images/individual_b.png"
            elif self.category == "group":
                image_path = "images/group_b.png"
        self.category_icon.icon = image_path
        self.set_contact_context_icons()




class NewContact(Window):
    def __init__(self, chat):
        super().__init__(
            size = (600, 150),
            resizable= False,
            closable=False
        )

        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.chat = chat

        self.is_valid_toggle = None

        self.title = "Add Contact"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self._impl.native.set_keep_above(True)
        self._impl.native.set_modal(True)

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )

        self.info_label = Label(
            text="Enter the message address",
            style=Pack(
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 11,
                padding_top = 5
            )
        )

        self.address_input = TextInput(
            placeholder="Z Address",
            style=Pack(
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                width = 450
            ),
            on_change=self.is_valid_address
        )

        self.is_valid = ImageView(
            style=Pack(
                width = 30,
                height = 30,
                padding= (1,0,0,10)
            )
        )

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                alignment = CENTER,
                padding = (10,0,10,0)
            )
        )

        self.cancel_button = Button(
            text="Cancel",
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                font_size = 12,
                alignment = CENTER,
                padding_bottom = 10,
                padding_right = 10
            ),
            on_press=self.close_new_contact
        )
        self.cancel_button._impl.native.connect("enter-notify-event", self.cancel_button_mouse_enter)
        self.cancel_button._impl.native.connect("leave-notify-event", self.cancel_button_mouse_leave)

        self.send_request_button = Button(
            text="Send Request",
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                font_size = 12,
                alignment = CENTER,
                padding_bottom = 10,
                padding_right = 10
            ),
            on_press=self.verify_address
        )
        self.send_request_button._impl.native.connect("enter-notify-event", self.send_request_button_mouse_enter)
        self.send_request_button._impl.native.connect("leave-notify-event", self.send_request_button_mouse_leave)

        self.buttons_box = Box(
            style=Pack(
                direction = ROW,
                alignment =CENTER
            )
        )

        self.content = self.main_box

        self.main_box.add(
            self.info_label,
            self.input_box,
            self.buttons_box
        )
        self.input_box.add(
            self.address_input,
            self.is_valid
        )
        self.buttons_box.add(
            self.cancel_button,
            self.send_request_button
        )


    async def is_valid_address(self, widget):
        address = self.address_input.value
        if not address:
            self.is_valid.image = None
            return
        if address.startswith("z"):
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

    
    def verify_address(self, button):
        address = self.address_input.value
        if not address:
            self.error_dialog(
                title="Address Required",
                message="Enter the contact address to proceed."
            )
            self.address_input.focus()
            return
        if not self.is_valid_toggle:
            self.error_dialog(
                title="Invalid Address",
                message="The address entered is not valid. Please check and try again."
            )
            return
        contacts = self.storage.get_contacts("address")
        if address in contacts:
            self.error_dialog(
                title="Address Already in Contacts",
                message="This address is already in your contacts list."
            )
            return
        pending = self.storage.get_pending()
        if address in pending:
            self.error_dialog(
                title="Address in Pending List",
                message="This address is already in your pending list."
            )
            return
        requests = self.storage.get_requests()
        if address in requests:
            self.error_dialog(
                title="Address in Requests",
                message="This address is already in your requests list."
            )
            return
        self.app.add_background_task(self.send_request)


    async def send_request(self, widget):
        destination_address = self.address_input.value
        amount = 0.0001
        txfee = 0.0001
        id = self.units.generate_id()
        category, username, address = self.storage.get_identity()
        memo = {"type":"request","category":category,"id":id,"username":username,"address":address}
        memo_str = json.dumps(memo)
        self.disable_window()
        await self.send_memo(
            address,
            destination_address,
            amount,
            txfee,
            memo_str,
            id
        )


    async def send_memo(self, address, toaddress, amount, txfee, memo, id):
        def on_result(widget, result):
            if result is None:
                self.chat.new_contact_toggle = None
                self.close()
        operation, _= await self.commands.SendMemo(address, toaddress, amount, txfee, memo)
        if operation:
            transaction_status, _= await self.commands.z_getOperationStatus(operation)
            transaction_status = json.loads(transaction_status)
            if isinstance(transaction_status, list) and transaction_status:
                status = transaction_status[0].get('status')
                if status == "executing" or status =="success":
                    await asyncio.sleep(1)
                    while True:
                        transaction_result, _= await self.commands.z_getOperationResult(operation)
                        transaction_result = json.loads(transaction_result)
                        if isinstance(transaction_result, list) and transaction_result:
                            result = transaction_result[0].get('result', {})
                            txid = result.get('txid')
                            self.storage.tx(txid)
                            self.storage.add_request(id, toaddress)
                            self.info_dialog(
                                title="Request sent",
                                message="The request has been sent successfully to the address.",
                                on_result=on_result
                            )
                            return
                        await asyncio.sleep(3)
                else:
                    self.enable_window()
        else:
            self.enable_window()

    
    def disable_window(self):
        self.address_input.readonly = True
        self.cancel_button.enabled = False
        self.send_request_button.enabled = False

    def enable_window(self):
        self.address_input.readonly = False
        self.cancel_button.enabled = True
        self.send_request_button.enabled = True

    def send_request_button_mouse_enter(self, widget, event):
        self.send_request_button.style.color = BLACK
        self.send_request_button.style.background_color = GREENYELLOW

    def send_request_button_mouse_leave(self, widget, event):
        self.send_request_button.style.color = GRAY
        self.send_request_button.style.background_color = TRANSPARENT


    def cancel_button_mouse_enter(self, sender, event):
        self.cancel_button.style.color = WHITE
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, sender, event):
        self.cancel_button.style.color = GRAY
        self.cancel_button.style.background_color = TRANSPARENT

    def close_new_contact(self, button):
        self.close()




class Pending(Box):
    def __init__(self, category, contact_id, username, address, app:App, window:Window, chat:Box):
        super().__init__(
            style=Pack(
                direction = ROW,
                padding = (5,5,0,5),
                height = 50
            )
        )

        self.app = app
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.storage = Storage(self.app)
        self.pending_window = window
        self.chat = chat

        self.category = category
        self.contact_id = contact_id
        self.username = username
        self.address = address

        if self.utils.get_sys_mode():
            if self.category == "individual":
                image_path = "images/individual_w.png"
            elif self.category == "group":
                image_path = "images/group_w.png"
        else:
            if self.category == "individual":
                image_path = "images/individual_b.png"
            elif self.category == "group":
                image_path = "images/group_b.png"

        self.category_icon = ImageView(
            image=image_path,
            style=Pack(
                padding = (13,0,0,10)
            )
        )

        self.username_label = Label(
            text=self.username,
            style=Pack(
                flex = 1,
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                padding_top = 20
            )
        )

        self.confirm_button = Button(
            text="Confirm",
            style=Pack(
                font_weight = BOLD,
                padding_top = 14
            ),
            on_press=self.send_identity
        )

        self.reject_button = Button(
            text="Reject",
            style=Pack(
                font_weight = BOLD,
                padding = (14,10,0,10)
            ),
            on_press=self.reject_pending
        )

        self.add(
            self.category_icon,
            self.username_label,
            self.confirm_button,
            self.reject_button
        )


    async def send_identity(self, button):
        self.disable_button()
        destination_address = self.address
        amount = Decimal('0.0001')
        txfee = Decimal('0.0001')
        category, username, address = self.storage.get_identity()
        id = self.units.generate_id()
        memo = {"type":"identity","category":category,"id":id,"username":username,"address":address}
        memo_str = json.dumps(memo)
        await self.send_memo(
            address,
            destination_address,
            amount,
            txfee,
            memo_str,
            id
        )


    async def send_memo(self, address, toaddress, amount, txfee, memo, id):
        def on_result(widget, result):
            if result is None:
                self.enable_button()
                self.pending_window.pending_list_box.remove(self)
        operation, _= await self.commands.SendMemo(address, toaddress, amount, txfee, memo)
        if operation:
            transaction_status, _= await self.commands.z_getOperationStatus(operation)
            transaction_status = json.loads(transaction_status)
            if isinstance(transaction_status, list) and transaction_status:
                status = transaction_status[0].get('status')
                if status == "executing" or status =="success":
                    await asyncio.sleep(1)
                    while True:
                        transaction_result, _= await self.commands.z_getOperationResult(operation)
                        transaction_result = json.loads(transaction_result)
                        if isinstance(transaction_result, list) and transaction_result:
                            result = transaction_result[0].get('result', {})
                            txid = result.get('txid')
                            self.storage.tx(txid)
                            self.storage.delete_pending(self.address)
                            self.storage.add_contact(self.category, id, self.contact_id, self.username, self.address)
                            self.pending_window.info_dialog(
                                title="New Contact Added",
                                message="The contact has been successfully stored in the list.",
                                on_result=on_result
                            )
                            return
                        await asyncio.sleep(3)
                else:
                    self.enable_button()
        else:
            self.enable_button()


    def reject_pending(self, button):
        self.storage.ban(self.address)
        self.storage.delete_pending(self.address)
        self.pending_window.pending_list_box.remove(self)


    def disable_button(self):
        self.confirm_button.enabled = False
        self.reject_button.enabled = False
        self.window.close_button.enabled = False

    def enable_button(self):
        self.confirm_button.enabled = True
        self.reject_button.enabled = True
        self.window.close_button.enabled = True




class PendingList(Window):
    def __init__(self, chat:Box):
        super().__init__(
            size = (500, 400),
            resizable= False,
            closable=False
        )

        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.chat = chat

        self.title = "Pending List"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self._impl.native.set_keep_above(True)
        self._impl.native.set_modal(True)

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )

        self.no_pending_label = Label(
            text="Empty list",
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                font_size = 10,
                flex = 1,
                text_align = CENTER
            )
        )

        self.no_pending_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                alignment = CENTER
            )
        )

        self.pending_list_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )

        self.pending_list = ScrollContainer(
            horizontal=None,
            style=Pack(
                flex = 1
            )
        )

        self.close_button = Button(
            text="Close",
            style=Pack(
                color = GRAY,
                font_size = 12,
                font_weight = BOLD,
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_pinding_list
        )
        self.close_button._impl.native.connect("enter-notify-event", self.close_button_mouse_enter)
        self.close_button._impl.native.connect("leave-notify-event", self.close_button_mouse_leave)

        self.content = self.main_box

        self.get_pending_list()

    def get_pending_list(self):
        pending = self.storage.get_pending()
        if pending:
            for data in pending:
                category = data[0]
                id = data[1]
                username = data[2]
                address = data[3]
                pending_contact = Pending(
                    category=category,
                    contact_id=id,
                    username=username,
                    address=address,
                    app = self.app,
                    window = self,
                    chat = self.chat
                )
                self.pending_list_box.add(
                    pending_contact
                )
            self.pending_list.content = self.pending_list_box
            self.main_box.add(
                self.pending_list,
                self.close_button
            )
        else:
            self.main_box.add(
                self.no_pending_box,
                self.close_button
            )
            self.no_pending_box.add(
                self.no_pending_label
            )

    def insert_pending(self, category, id, username, address):
        pending_contact = Pending(
            category=category,
            contact_id=id,
            username=username,
            address=address,
            window = self
        )
        self.pending_list_box.add(pending_contact)


    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = WHITE
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = GRAY
        self.close_button.style.background_color = TRANSPARENT


    def close_pinding_list(self, button):
        self.chat.pending_toggle = None
        self.close()



class Chat(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                padding = (2,5,0,5),
                flex = 1
            )
        )

        self.app = app
        self.main = main
        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.clipboard = ClipBoard()
        self.settings = Settings(self.app)
        
        self.send_toggle = None
        self.contact_id = None
        self.user_address = None
        self.selected_contact_toggle = None
        self.pending_toggle = None
        self.new_contact_toggle = None
        self.new_pending_toggle = None
        self.scroll_toggle = None
        self.unread_messages_toggle = None
        self.last_message_timestamp = None
        self.last_unread_timestamp = None
        self.messages = []
        self.unread_messages = []
        self.processed_timestamps = set()

        if self.utils.get_sys_mode():
            add_contact_icon = "images/add_contact_w"
            pending_icon = "images/pending_w"
            copy_icon = "images/copy_w"
            panel_color = rgb(56,56,56)
        else:
            add_contact_icon = "images/add_contact_b"
            pending_icon = "images/pending_b"
            copy_icon = "images/copy_b"
            panel_color = rgb(230,230,230)

        self.add_contact = Button(
            icon=add_contact_icon,
            on_press=self.add_contact_click
        )
        self.add_contact._impl.native.set_tooltip_text("Add new contact")

        self.pending_contacts = Button(
            icon=pending_icon,
            on_press=self.pending_contacts_click
        )
        self.pending_contacts._impl.native.set_tooltip_text("Show pending contacts")

        self.copy_address = Button(
            icon=copy_icon,
            on_press=self.copy_messages_address
        )
        self.copy_address._impl.native.set_tooltip_text("Copy your messages address")

        self.buttons_box = Box(
            style=Pack(
                alignment = CENTER,
                direction = ROW,
                height = 42
            )
        )

        self.address_balance = Label(
            text = f"Balance : 0.00000000",
            style=Pack(
                color = rgb(114,137,218),
                background_color = panel_color,
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 8,
                flex = 1
            )
        )

        self.info_box = Box(
            style=Pack(
                alignment = CENTER,
                direction = ROW,
                background_color = panel_color,
                height = 42,
                flex = 1
            )
        )

        self.contacts_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1
            )
        )

        self.contacts_scroll = ScrollContainer(
            horizontal=False,
            style=Pack(
                padding_top = 5,
                flex = 1
            )
        )

        self.panel_box = Box(
            style=Pack(
                direction = COLUMN,
                width = 300
            )
        )

        self.contact_info_box = Box(
            style=Pack(
                direction = ROW,
                background_color = panel_color,
                height = 42,
                alignment = CENTER
            )
        )

        self.messages_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1
            )
        )

        self.output_box = ScrollContainer(
            horizontal=False,
            style=Pack(
                flex = 1,
                padding_bottom = 5
            )
        )
        v_adjustment = self.output_box._impl.native.get_vadjustment()
        v_adjustment.connect("value-changed", self.update_messages_on_scroll)

        self.message_input = TextInput(
            placeholder="Write message",
            style=Pack(
                font_size = 11,
                font_weight = BOLD,
                flex = 1,
                padding =(0,0,5,5)
            ),
            on_change=self.update_character_count,
            on_confirm=self.verify_message
        )

        self.character_count = Label(
            text="Limit : 0 / 325",
            style=Pack(
                color = GRAY,
                text_align = CENTER,
                font_size = 10,
                font_weight = BOLD
            )
        )

        self.fee_input = TextInput(
            value="0.00020000",
            style=Pack(
                font_size = 10,
                font_weight = BOLD,
                padding_bottom = 2,
                text_align = CENTER
            )
        )

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                alignment = BOTTOM
            )
        )

        self.options_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = CENTER
            )
        )

        self.send_button = Button(
            text="Send",
            style=Pack(
                color = GRAY,
                font_size = 12,
                font_weight = BOLD,
                width = 168
            ),
            on_press=self.verify_message
        )
        self.send_button._impl.native.connect("enter-notify-event", self.send_button_mouse_enter)
        self.send_button._impl.native.connect("leave-notify-event", self.send_button_mouse_leave)

        self.send_box = Box(
            style=Pack(
                direction = ROW,
                alignment = BOTTOM
            )
        )

        self.chat_buttons = Box(
            style=Pack(
                direction = COLUMN,
                padding = 5
            )
        )

        self.chat_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 7,
                padding_left = 5
            )
        )
        self.add(
            self.panel_box,
            self.chat_box
        )
        self.contacts_scroll.content = self.contacts_box
        self.panel_box.add(
            self.buttons_box,
            self.contacts_scroll
        )
        self.buttons_box.add(
            self.add_contact,
            self.pending_contacts,
            self.copy_address,
            self.info_box
        )
        self.info_box.add(
            self.address_balance
        )
        self.output_box.content = self.messages_box
        self.chat_box.add(
            self.contact_info_box,
            self.output_box,
            self.input_box
        )
        self.input_box.add(
            self.message_input,
            self.chat_buttons
        )
        self.chat_buttons.add(
            self.options_box,
            self.send_box
        )
        self.options_box.add(
            self.character_count,
            self.fee_input
        )
        self.send_box.add(
            self.send_button
        )

    
    def run_tasks(self):
        self.app.add_background_task(self.update_messages_balance)
        self.app.add_background_task(self.waiting_new_memos)
        self.app.add_background_task(self.update_contacts_list)
        self.app.add_background_task(self.character_count_zero)
        self.load_pending_list()


    async def update_messages_balance(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue
            address = self.storage.get_identity("address")
            if address:
                balance, _= await self.commands.z_getBalance(address[0])
                if balance:
                    balance = self.units.format_balance(balance)
                    self.address_balance.text = f"Balance : {balance}"
            
            await asyncio.sleep(5)


    async def waiting_new_memos(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            address = self.storage.get_identity("address")
            if address:
                listunspent, _= await self.commands.z_listUnspent(address[0], 0)
                if listunspent:
                    listunspent = json.loads(listunspent)
                    if len(listunspent) >= 54:
                        total_balance,_ = await self.commands.z_getBalance(address[0])
                        merge_fee = Decimal('0.0002')
                        txfee = Decimal('0.0001')
                        amount = Decimal(total_balance) - merge_fee
                        await self.merge_utxos(address[0], amount, txfee)
                    list_txs = self.storage.get_txs()
                    for data in listunspent:
                        txid = data['txid']
                        if txid not in list_txs:
                            await self.unhexlify_memo(data)

            await asyncio.sleep(5)



    async def merge_utxos(self, address, amount, txfee):
        memo = "merge"
        operation, _= await self.commands.SendMemo(address, address, amount, txfee, memo)
        if operation:
            transaction_status, _= await self.commands.z_getOperationStatus(operation)
            transaction_status = json.loads(transaction_status)
            if isinstance(transaction_status, list) and transaction_status:
                status = transaction_status[0].get('status')
                if status == "executing" or status =="success":
                    await asyncio.sleep(1)
                    while True:
                        transaction_result, _= await self.commands.z_getOperationResult(operation)
                        transaction_result = json.loads(transaction_result)
                        if isinstance(transaction_result, list) and transaction_result:
                            status = transaction_result[0].get('status')
                            result = transaction_result[0].get('result', {})
                            if status == "failed":
                                    return
                            txid = result.get('txid')
                            self.storage.tx(txid)
                            return
                        await asyncio.sleep(3)


    async def unhexlify_memo(self, data):
        memo = data['memo']
        amount = data['amount']
        txid = data['txid']
        try:
            decoded_memo = binascii.unhexlify(memo)
            form = decoded_memo.decode('utf-8')
            clean_form = form.rstrip('\x00')
            form_dict = json.loads(clean_form)
            form_type = form_dict.get('type')

            if form_type == "identity":
                await self.get_identity(form_dict)
                self.storage.tx(txid)
            elif form_type == "message":
                await self.get_message(form_dict, amount)
                self.storage.tx(txid)
            elif form_type == "request":
                await self.get_request(form_dict)
                self.storage.tx(txid)

        except (binascii.Error, json.decoder.JSONDecodeError) as e:
            self.storage.tx(txid)
            print(f"Received new transaction. Amount: {amount}")
        except Exception as e:
            self.storage.tx(txid)
            print(f"Received new transaction. Amount: {amount}")
    

    async def get_identity(self, form):
        category = form.get('category')
        contact_id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        if address in banned:
            return
        id = self.storage.get_request(address)
        if id:
            self.storage.add_contact(category, id[0], contact_id, username, address)
            self.storage.delete_request(address)
            if self.settings.notification_messages():
                try:
                    notify = NotifyGtk(
                        title="Request Accepted",
                        message=f"By {username}",
                        duration=5
                    )
                    notify.popup()
                except Exception:
                    pass


    async def get_message(self, form, amount):
        contact_id = form.get('id')
        author = form.get('username')
        message = form.get('text')
        timestamp = form.get('timestamp')
        contact_username = self.storage.get_contact_username(contact_id)
        if not contact_username:
            return
        self.processed_timestamps.add(timestamp)
        if author != contact_username:
            self.storage.update_contact_username(author, contact_id)
        if self.contact_id == contact_id and self.main.message_button_toggle:
            self.storage.message(contact_id, author, message, amount, timestamp)
        else:
            self.unread_messages_toggle = True
            self.storage.unread_message(contact_id, author, message, amount, timestamp)
            if self.settings.notification_messages():
                try:
                    notify = NotifyGtk(
                        title="New Message",
                        message=f"From : {author}",
                        duration=5
                    )
                    notify.popup()
                except Exception:
                    pass
        


    async def get_request(self, form):
        category = form.get('category')
        contact_id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        if address in banned:
            return
        self.storage.add_pending(category, contact_id, username, address)
        if not self.pending_toggle:
            self.update_pending_list()
        else:
            self.pending_list.insert_pending(category, contact_id, username, address)
        if self.settings.notification_messages():
            try:
                notify = NotifyGtk(
                    title="New Request",
                    message=f"From : {username}",
                    duration=5
                )
                notify.popup()
            except Exception:
                pass


    async def update_contacts_list(self, widget):
        self.contacts = []
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue
            contacts = self.storage.get_contacts()
            if contacts:
                for data in contacts:
                    try:
                        category = data[0]
                        contact_id = data[2]
                        username = data[3]
                        address = data[4]
                        if contact_id not in self.contacts:
                            contact = Contact(
                                category=category,
                                contact_id=contact_id,
                                username=username,
                                address=address,
                                app = self.app,
                                chat = self,
                                main = self.main
                            )
                            
                            self.contacts_box.add(
                                contact
                            )
                            self.contacts.append(contact_id)
                            contact.category_icon.on_press = partial(self.contact_click, contact_id=contact_id, address=address)
                            contact.username_label.on_press = partial(self.contact_click, contact_id=contact_id, address=address)
                    except IndexError:
                        print(f"Skipping contact due to missing data: {data}")
                        continue
                    except Exception as e:
                        print(f"Unexpected error: {e}, data: {data}")
                        continue
            await asyncio.sleep(5)


    def load_pending_list(self):
        pending = self.storage.get_pending()
        if pending:
            if self.utils.get_sys_mode():
                icon = "images/new_pending_w"
            else:
                icon = "images/new_pending_b"
            self.pending_contacts.icon = icon
            self.new_pending_toggle = True


    async def contact_click(self, button, contact_id, address):
        if self.send_toggle:
            return
        if self.contact_id == contact_id:
            return
        username = self.storage.get_contact_username(contact_id)
        if self.selected_contact_toggle:
            self.contact_info_box.clear()
            self.messages_box.clear()
            self.last_message_timestamp = None
            self.last_unread_timestamp = None
        self.selected_contact_toggle = True
        self.processed_timestamps.clear()
        username_label = Label(
            text="Username :",
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                padding = (11,0,0,10)
            )
        )
        self.username_value = Label(
            text=username[0],
            style=Pack(
                font_weight = BOLD,
                padding = (11,0,0,5)
            )
        )
        id_label = Label(
            text="ID :",
            style=Pack(
                color = GRAY,
                font_weight = BOLD,
                padding = (11,0,0,10)
            )
        )
        id_value = Label(
            text=contact_id,
            style=Pack(
                font_weight = BOLD,
                padding = (11,0,0,5),
                flex =1
            )
        )
        self.unread_label = Label(
            text="--Unread Messages--",
            style=Pack(
                font_weight = BOLD,
                font_size = 10,
                text_align = CENTER,
                flex =1,
                padding = (0,30,5,15)
            )
        )
        self.contact_info_box.add(
            username_label,
            self.username_value,
            id_label,
            id_value
        )
        self.contact_id = contact_id
        self.user_address = address

        self.messages = self.storage.get_messages(self.contact_id)
        self.unread_messages = self.storage.get_unread_messages(self.contact_id)
        if self.messages:
            messages = sorted(self.messages, key=lambda x: x[3], reverse=True)
            recent_messages = messages[:5]
            self.last_message_timestamp = recent_messages[-1][3]
            for data in recent_messages:
                message_username = data[0]
                message_text = data[1]
                message_amount = data[2]
                message_timestamp = data[3]
                self.processed_timestamps.add(message_timestamp)
                message = Message(
                    author=message_username,
                    message=message_text,
                    amount=message_amount,
                    timestamp=message_timestamp,
                    app= self.app,
                    output = self.output_box
                )
                self.messages_box.insert(
                    0, message
                )
            await asyncio.sleep(0.1)
            self.output_box.vertical_position = self.output_box.max_vertical_position
        if self.unread_messages:
            unread_messages = sorted(self.unread_messages, key=lambda x: x[3])
            recent_unread_messages = unread_messages[:5]
            self.last_unread_timestamp = recent_unread_messages[-1][3]
            self.messages_box.add(
                self.unread_label
            )
            for data in unread_messages:
                message_username = data[0]
                message_text = data[1]
                message_amount = data[2]
                message_timestamp = data[3]
                self.processed_timestamps.add(message_timestamp)
                message = Message(
                    author=message_username,
                    message=message_text,
                    amount=message_amount,
                    timestamp=message_timestamp,
                    app= self.app,
                    output = self.output_box
                )
                self.messages_box.add(
                    message
                )
        self.app.add_background_task(self.update_current_messages)


    async def update_current_messages(self, widget):
        self.messages = self.storage.get_messages(self.contact_id)
        self.unread_messages = self.storage.get_unread_messages(self.contact_id)
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue

            messages = self.storage.get_messages(self.contact_id)
            if messages:
                for data in messages:
                    if data not in self.messages:
                        author = data[0]
                        text = data[1]
                        amount = data[2]
                        timestamp = data[3]
                        await self.insert_message(author, text, amount, timestamp)
                        self.messages.append(data)

            unread_messages = self.storage.get_unread_messages(self.contact_id)
            if unread_messages:
                for data in unread_messages:
                    if data not in self.unread_messages:
                        author = data[0]
                        text = data[1]
                        amount = data[2]
                        timestamp = data[3]
                        self.insert_unread_message(author, text, amount, timestamp)
                        self.unread_messages.append(data)
                
            await asyncio.sleep(3)


    def update_messages_on_scroll(self, adjustment):
        vertical_position = adjustment.get_value()
        min_value = adjustment.get_lower()
        max_value = adjustment.get_upper() - adjustment.get_page_size()
        if vertical_position <= min_value:
            if not self.scroll_toggle:
                self.app.add_background_task(self.load_old_messages)
                self.scroll_toggle = True
        elif vertical_position >= max_value:
            self.messages_box.remove(self.unread_label)
            self.clean_unread_messages()
            if not self.scroll_toggle:
                self.app.add_background_task(self.load_unread_messages)
                self.scroll_toggle = True
        


    def clean_unread_messages(self):
        unread_messages = self.storage.get_unread_messages(self.contact_id)
        if unread_messages:
            for data in unread_messages:
                author = data[0]
                text = data[1]
                amount = data[2]
                timestamp = data[3]
                self.storage.message(self.contact_id, author, text, amount, timestamp)
                self.messages.append(data)
            self.storage.delete_unread(self.contact_id)


    async def load_old_messages(self, widget):
        messages = self.storage.get_messages(self.contact_id)
        messages = sorted(messages, key=lambda x: x[3], reverse=True)
        last_loaded_message_timestamp = self.last_message_timestamp
        try:
            last_loaded_index = next(i for i, m in enumerate(messages) if m[3] == last_loaded_message_timestamp)
        except StopIteration:
            return
        older_messages = messages[last_loaded_index + 1 : last_loaded_index + 6]
        if older_messages:
            self.last_message_timestamp = older_messages[-1][3]
            for data in older_messages:
                message = Message(
                    author=data[0],
                    message=data[1],
                    amount=data[2],
                    timestamp=data[3],
                    app=self.app,
                    output=self.output_box
                )
                self.messages_box.insert(0, message)
            await asyncio.sleep(1)
        self.scroll_toggle = False


    async def load_unread_messages(self, widget):
        unread_messages = self.storage.get_unread_messages(self.contact_id)
        if unread_messages:
            unread_messages = sorted(unread_messages, key=lambda x: x[3], reverse=False)
            more_unread_messages = [m for m in unread_messages if m[3] < self.last_unread_timestamp]
            more_unread_messages = more_unread_messages[:5]

            for data in more_unread_messages:
                message_username = data[0]
                message_text = data[1]
                message_amount = data[2]
                message_timestamp = data[3]
                self.processed_timestamps.add(message_timestamp)
                message = Message(
                    author=message_username,
                    message=message_text,
                    amount=message_amount,
                    timestamp=message_timestamp,
                    app=self.app,
                    output=self.output_box
                )
                self.messages_box.add(message)

            if more_unread_messages:
                self.last_unread_timestamp = more_unread_messages[-1][3]
                await asyncio.sleep(1)
        self.scroll_toggle = False


    def add_contact_click(self, button):
        self.new_contact = NewContact(self)
        self.new_contact.show()


    def update_pending_list(self):
        pending = self.storage.get_pending()
        if pending:
            if not self.new_pending_toggle:
                mode = self.utils.get_sys_mode()
                if mode:
                    icon = "images/new_pending_w"
                else:
                    icon = "images/new_pending_b"
                self.pending_contacts.icon = icon
                self.new_pending_toggle = True


    def pending_contacts_click(self, button):
        if not self.pending_toggle and not self.new_contact_toggle:
            if self.new_pending_toggle:
                mode = self.utils.get_sys_mode()
                if mode:
                    pending_icon = "images/pending_w"
                else:
                    pending_icon = "images/pending_b"
                self.pending_contacts.icon = pending_icon
                self.new_pending_toggle = None
            self.pending_list = PendingList(self)
            self.pending_list.show()
            self.pending_toggle = True


    def copy_messages_address(self, button):
        address = self.storage.get_identity("address")
        self.clipboard.copy(address[0])
        self.main.info_dialog(
            title="Copied",
            message="The messages address has been copied to clipboard."
        )


    async def verify_message(self, button):
        message = self.message_input.value.strip()
        character_count = len(message)
        fee = self.fee_input.value
        if not message:
            self.message_input.value = ""
            self.main.info_dialog(
                title="Message Required",
                message="Enter a message before sending."
            )
            self.message_input.focus()
            return
        elif not self.selected_contact_toggle:
            self.main.error_dialog(
                title="No Contact Selected",
                message="Select a contact from the list before sending a message."
            )
            return
        elif character_count > 325:
            self.main.error_dialog(
                title="Message Too Long",
                message="Message exceeds the maximum length of 325 characters."
            )
            return
        elif float(fee) < 0.0002:
            self.main.error_dialog(
                title="Fee Too Low",
                message="The minimum fee per message is 0.0002."
            )
            self.fee_input.value = "0.00020000"
            return
        self.app.add_background_task(self.send_message)

    
    async def send_message(self, widget):
        author = "you"
        _, username, address = self.storage.get_identity()
        id = self.storage.get_id_contact(self.contact_id)
        message = self.message_input.value.replace('\n', '')
        fee = self.fee_input.value
        amount = float(fee) - 0.0001
        txfee = 0.0001
        timestamp = await self.get_message_timestamp()
        if timestamp is not None:
            memo = {"type":"message","id":id[0],"username":username,"text":message, "timestamp":timestamp}
            memo_str = json.dumps(memo)
            self.disable_send_button()
            await self.send_memo(
                address,
                amount,
                txfee,
                memo_str,
                author,
                message,
                timestamp
            )


    async def send_memo(self, address, amount, txfee, memo, author, text, timestamp):
        operation, _= await self.commands.SendMemo(address, self.user_address, amount, txfee, memo)
        if operation:
            transaction_status, _= await self.commands.z_getOperationStatus(operation)
            transaction_status = json.loads(transaction_status)
            if isinstance(transaction_status, list) and transaction_status:
                status = transaction_status[0].get('status')
                if status == "executing" or status =="success":
                    await asyncio.sleep(1)
                    while True:
                        transaction_result, _= await self.commands.z_getOperationResult(operation)
                        transaction_result = json.loads(transaction_result)
                        if isinstance(transaction_result, list) and transaction_result:
                            result = transaction_result[0].get('result', {})
                            txid = result.get('txid')
                            self.storage.tx(txid)
                            self.storage.message(self.contact_id, author, text, amount, timestamp)
                            self.message_input.value = ""
                            self.fee_input.value = "0.00020000"
                            return
                        await asyncio.sleep(3)
                else:
                    self.enable_send_button()
        else:
            self.enable_send_button()
    

    def enable_send_button(self):
        self.send_toggle = False
        self.send_button.enabled = True
        self.message_input.readonly = False

    
    def disable_send_button(self):
        self.send_toggle = True
        self.send_button.enabled = False
        self.message_input.readonly = True


    async def insert_message(self, author, text, amount, timestamp):
        message = Message(
            author=author,
            message=text,
            amount=amount,
            timestamp=timestamp,
            app=self.app,
            output=self.output_box
        )
        self.messages_box.add(
            message
        )
        await asyncio.sleep(0.1)
        self.output_box.vertical_position = self.output_box.max_vertical_position
        self.enable_send_button()

    
    def insert_unread_message(self, author, text, amount, timestamp):
        message = Message(
            author=author,
            message=text,
            amount=amount,
            timestamp=timestamp,
            app=self.app,
            output=self.output_box
        )
        self.messages_box.add(
            message
        )


    def update_character_count(self, input):
        message = self.message_input.value
        character_count = len(message)
        if character_count > 325:
            self.character_count.style.color = RED
        elif character_count < 325:
            self.character_count.style.color = GRAY
        elif character_count == 325:
            self.character_count.style.color = ORANGE
        self.character_count.text = f"Limit : {character_count} / 325"


    async def character_count_zero(self, widget):
        while True:
            message = self.message_input.value
            if not message:
                self.character_count.text = f"Limit : 0 / 325"

            await asyncio.sleep(1)


    def send_button_mouse_enter(self, widget, event):
        self.send_button.style.color = BLACK
        self.send_button.style.background_color = rgb(114,137,218)

    def send_button_mouse_leave(self, widget, event):
        self.send_button.style.color = GRAY
        self.send_button.style.background_color = TRANSPARENT


    async def get_message_timestamp(self):
        blockchaininfo, _ = await self.commands.getBlockchainInfo()
        if blockchaininfo is not None:
            if isinstance(blockchaininfo, str):
                info = json.loads(blockchaininfo)
                if info is not None:
                    timestamp = info.get('mediantime')
                    if timestamp in self.processed_timestamps:
                        highest_timestamp = max(self.processed_timestamps)
                        timestamp = highest_timestamp + 1
                    self.processed_timestamps.add(timestamp)
                    return timestamp
        


class Messages(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                flex = 1,
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.utils = Utils(self.app)
        self.chat = Chat(self.app, self.main)

        self.messages_toggle = None
        self.request_count = 0
        self.message_count = 0
        self.processed_timestamps = set()

        
    async def insert_widgets(self, widget):
        if not self.messages_toggle:
            data = self.storage.is_exists()
            if data:
                identity = self.storage.get_identity()
                if identity:
                    self.add(
                        self.chat
                    )
                else:
                    self.create_new_messenger()
            else:
                self.create_new_messenger()
            self.messages_toggle = True


    def create_new_messenger(self):
        self.new_messenger = NewMessenger(self, self.main, self.chat)
        self.add(self.new_messenger)


    async def gather_unread_memos(self):
        data = self.storage.is_exists()
        if data:
            address = self.storage.get_identity("address")
            if address:
                listunspent, _= await self.commands.z_listUnspent(address[0], 0)
                if listunspent:
                    listunspent = json.loads(listunspent)
                    list_txs = self.storage.get_txs()
                    for data in listunspent:
                        txid = data['txid']
                        if txid not in list_txs:
                            await self.unhexlify_memo(data)

                    if self.request_count > 0:
                        try:
                            notify = NotifyGtk(
                                title="New Request(s)",
                                message=f"{self.request_count} New Request(s)",
                                duration=5
                            )
                            notify.popup()
                        except Exception:
                            pass
                    if self.message_count > 0:
                        try:
                            notify = NotifyGtk(
                                title="New Messages(s)",
                                message=f"{self.message_count} New Message(s)",
                                duration=5
                            )
                            notify.popup()
                        except Exception:
                            pass

                    self.chat.run_tasks()


    async def unhexlify_memo(self, data):
        memo = data['memo']
        amount = data['amount']
        txid = data['txid']
        try:
            decoded_memo = binascii.unhexlify(memo)
            form = decoded_memo.decode('utf-8')
            clean_form = form.rstrip('\x00')
            form_dict = json.loads(clean_form)
            form_type = form_dict.get('type')

            if form_type == "message":
                await self.get_message(form_dict, amount)
                self.storage.tx(txid)
                self.message_count += 1
            elif form_type == "request":
                await self.get_request(form_dict)
                self.storage.tx(txid)
                self.request_count += 1

        except (binascii.Error, json.decoder.JSONDecodeError) as e:
            self.storage.tx(txid)
            print(f"Received new transaction. Amount: {amount}")
        except Exception as e:
            self.storage.tx(txid)
            print(f"Received new transaction. Amount: {amount}")


    async def get_message(self, form, amount):
        id = form.get('id')
        author = form.get('username')
        message = form.get('text')
        timestamp = form.get('timestamp')
        contacts_ids = self.storage.get_contacts("contact_id")
        if id not in contacts_ids:
            return
        self.storage.unread_message(id, author, message, amount, timestamp)
        self.chat.processed_timestamps.add(timestamp)


    async def get_request(self, form):
        category = form.get('category')
        id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        if address in banned:
            return
        self.storage.add_pending(category, id, username, address)
    

    def update_messages_mode(self, widget):
        if self.utils.get_sys_mode():
            if self.chat.new_pending_toggle:
                pending_icon = "images/new_pending_w"
            else:
                pending_icon = "images/pending_w"
            add_contact_icon = "images/add_contact_w"
            copy_icon = "images/copy_w"
            panel_color = rgb(56,56,56)
        else:
            if self.chat.new_pending_toggle:
                pending_icon = "images/new_pending_b"
            else:
                pending_icon = "images/pending_b"
            add_contact_icon = "images/add_contact_b"
            copy_icon = "images/copy_b"
            panel_color = rgb(230,230,230)
        self.chat.add_contact.icon = add_contact_icon
        self.chat.pending_contacts.icon = pending_icon
        self.chat.copy_address.icon = copy_icon
        self.chat.info_box.style.background_color = panel_color
        self.chat.address_balance.style.background_color = panel_color
        self.chat.contact_info_box.style.background_color = panel_color
        for widget in self.chat.contacts_box.children:
            self.app.add_background_task(widget.update_contact_mode)