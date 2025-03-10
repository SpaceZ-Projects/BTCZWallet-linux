
import asyncio
import json
import binascii

from toga import (
    App, Box, Window, Button, Label, TextInput,
    ScrollContainer, ImageView
)
from ..framework import ClipBoard, NotifyGtk
from toga.style.pack import Pack
from toga.constants import ROW, CENTER, COLUMN, BOLD
from toga.colors import rgb, BLACK, GRAY, WHITE, RED

from .storage import Storage
from .utils import Utils
from .client import Client



class Indentifier(Window):
    def __init__(self, messages_page:Box, main:Window, chat:Box):
        super().__init__(
            size = (700, 150),
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
                color = BLACK,
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
                color = BLACK,
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

        self.close_button = Button(
            text="Close",
            style=Pack(
                font_weight = BOLD,
                font_size = 12,
                alignment = CENTER,
                padding_bottom = 10,
                padding_right = 10
            )
        )

        self.confirm_button = Button(
            text="Confirm",
            style=Pack(
                font_weight = BOLD,
                font_size = 12,
                alignment = CENTER,
                padding_bottom = 10,
                padding_left = 10
            ),
            on_press=self.verify_identity
        )

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
            self.close_button,
            self.confirm_button
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
        category = "individual"
        username = self.username_input.value
        messages_address, _ = await self.commands.z_getNewAddress()
        if messages_address:
            prv_key, _= await self.commands.z_ExportKey(messages_address)
            if prv_key:
                self.storage.key(prv_key)
            self.storage.identity(category, username, messages_address)
            self.close()
            self.messages_page.clear()
            await asyncio.sleep(0.5)
            self.main.info_dialog(
                title="Identity Setup Complete!",
                message=f"Success! Your new identity has been securely set up with the username:\n\n"
                        f"Username: {username}\nAddress: {messages_address}\n\n"
                        "Your messages address and private key have been stored."
            )
            self.messages_page.add(self.chat)


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
                color = BLACK,
                font_weight = BOLD,
                font_size = 11
            )
        )
        self.create_button = Button(
            text="New Messenger",
            style=Pack(
                color = BLACK,
                font_weight = BOLD,
                font_size = 12,
                width = 160,
                padding_top = 7
            ),
            on_press=self.create_button_click
        )

        self.add(
            self.new_label,
            self.create_button
        )


    def create_button_click(self, button):
        if not self.new_identity_toggel:
            self.indentity = Indentifier(self.messages_page, self.main, self.chat)
            self.indentity.on_close = self.close_indentity_setup
            self.indentity.close_button.on_press = self.close_indentity_setup
            self.indentity.show()
            self.new_identity_toggel = True


    def close_indentity_setup(self, button):
        self.indentity.close()
        self.new_identity_toggel = None



class Contact(Box):
    def __init__(self, category, contact_id, username, address, app:App, chat, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 50
            )
        )

        self.app =app
        self.chat = chat
        self.main = main
        self.storage = Storage(self.app)
        self.clipboard = ClipBoard()

        self.category = category
        self.contact_id = contact_id
        self.username = username
        self.address = address

        if self.category == "individual":
            image_path = "images/individual.png"
        elif self.category == "group":
            image_path = "images/group.png"

        self.category_icon = ImageView(
            image=image_path,
            style=Pack(
                background_color = rgb(230,230,230),
                padding_left = 10
            )
        )

        self.username_label = Label(
            text=self.username,
            style=Pack(
                color = WHITE,
                background_color = rgb(230,230,230),
                flex = 1,
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                padding_top = 11
            )
        )

        self.unread_messages = Label(
            text="",
            style=Pack(
                color = WHITE,
                background_color = RED,
                text_align = CENTER,
                font_size = 9,
                font_weight = BOLD,
                padding =(15,20,0,0)
            )
        )

        self.add(
            self.category_icon,
            self.username_label,
            self.unread_messages
        )
        self.app.add_background_task(self.update_contact)


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




class NewContact(Window):
    def __init__(self):
        super().__init__(
            size = (600, 150),
            resizable= False,
            closable=False
        )

        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.storage = Storage(self.app)

        self.is_valid_toggle = None

        self.title = "Add Contact"
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

        self.close_button = Button(
            text="Close",
            style=Pack(
                font_weight = BOLD,
                font_size = 12,
                alignment = CENTER,
                padding_bottom = 10,
                padding_right = 10,
                width = 100
            )
        )

        self.confirm_button = Button(
            text="Confirm",
            style=Pack(
                font_weight = BOLD,
                font_size = 12,
                alignment = CENTER,
                padding_bottom = 10,
                padding_right = 10,
                width = 100
            ),
            on_press=self.verify_address
        )

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
            self.close_button,
            self.confirm_button
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
        id = self.utils.generate_id()
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
                                message="The request has been sent successfully to the address."
                            )
                            self.close()
                            return
                        await asyncio.sleep(3)
                else:
                    self.enable_window()
        else:
            self.enable_window()

    
    def disable_window(self):
        self.address_input.readonly = True
        self.close_button.enabled = False
        self.confirm_button.enabled = False

    def enable_window(self):
        self.address_input.readonly = False
        self.close_button.enabled = True
        self.confirm_button.enabled = True




class Pending(Box):
    def __init__(self, category, contact_id, username, address, app:App, window:Window, chat:Box):
        super().__init__(
            style=Pack(
                direction = ROW,
                background_color = rgb(40,43,48),
                padding = (5,5,0,5),
                height = 50
            )
        )

        self.app = app
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.storage = Storage(self.app)
        self.pending_window = window
        self.chat = chat

        self.category = category
        self.contact_id = contact_id
        self.username = username
        self.address = address

        if self.category == "individual":
            image_path = "images/individual.png"
        elif self.category == "group":
            image_path = "images/group.png"

        self.category_icon = ImageView(
            image=image_path,
            style=Pack(
                padding_left = 10
            )
        )

        self.username_label = Label(
            text=self.username,
            style=Pack(
                flex = 1,
                text_align = CENTER,
                font_size = 12,
                font_weight = BOLD,
                padding_top = 11
            )
        )

        self.confirm_button = ImageView(
            image="images/confirm_i.png",
            style=Pack(
                background_color = rgb(40,43,48),
                padding_top = 14
            )
        )

        self.reject_button = ImageView(
            image="images/reject_i.png",
            style=Pack(
                background_color = rgb(40,43,48),
                padding = (14,10,0,10)
            )
        )

        self.add(
            self.category_icon,
            self.username_label,
            self.confirm_button,
            self.reject_button
        )


    def confirm_button_click(self, sender, event):
        self.app.add_background_task(self.send_identity)


    async def send_identity(self, widget):
        destination_address = self.address
        amount = 0.0001
        txfee = 0.0001
        category, username, address = self.storage.get_identity()
        id = self.utils.generate_id()
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
                            self.pending_window.pending_list_box.remove(self)
                            self.pending_window.info_dialog(
                                title="New Contact Added",
                                message="The contact has been successfully stored in the list."
                            )
                            return
                        await asyncio.sleep(3)
                else:
                    pass
        else:
            pass


    def reject_button_click(self, sender, event):
        self.storage.ban(self.address)
        self.storage.delete_pending(self.address)
        self.pending_window.pending_list_box.remove(self)


    def show_pending_info(self, sender, event):
        self.pending_window.info_dialog(
            title = "Pending info",
            message = f"- Username : {self.username}\n- ID : {self.contact_id}\n- Address : {self.address}"
        )





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
                font_weight = BOLD,
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            )
        )

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
            self.main_box.add(
                self.pending_list,
                self.close_button
            )
            self.pending_list.content = self.pending_list_box
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
        self.commands = Client(self.app)
        self.storage = Storage(self.app)
        self.clipboard = ClipBoard()
        
        self.contact_id = None
        self.new_contact_toggle = None
        self.pending_toggle = None
        self.new_pending_toggle = None
        self.processed_timestamps = set()

        mode = self.utils.get_sys_mode()
        if mode:
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

        self.input_box = Box(
            style=Pack(
                direction = ROW,
                background_color = panel_color,
                height = 100
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

    
    def run_tasks(self):
        self.app.add_background_task(self.update_messages_balance)
        self.app.add_background_task(self.waiting_new_memos)


    async def update_messages_balance(self, widget):
        while True:
            if not self.main.message_button_toggle:
                await asyncio.sleep(1)
                continue
            address = self.storage.get_identity("address")
            if address:
                balance, _= await self.commands.z_getBalance(address[0])
                if balance:
                    balance = self.utils.format_balance(balance)
                    self.address_balance.text = f"Balance : {balance}"
            
            await asyncio.sleep(5)


    async def waiting_new_memos(self, widget):
        while True:
            address = self.storage.get_identity("address")
            if address:
                listunspent, _= await self.commands.z_listUnspent(address[0])
                if listunspent:
                    listunspent = json.loads(listunspent)
                    if len(listunspent) >= 54:
                        total_balance,_ = await self.commands.z_getBalance(address[0])
                        merge_fee = 0.0002
                        txfee = 0.0001
                        amount = float(total_balance) - merge_fee
                        await self.merge_utxos(address[0], amount, txfee)
                        return
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


    async def get_transaction_timerecived(self, txid):
        transaction = await self.commands.getTransaction(txid)
        json_str = transaction[0]
        data = json.loads(json_str)
        timerecived = data.get("timereceived", None)
        return timerecived
    

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
            notify = NotifyGtk(
                title="Request Accepted",
                message=f"By {username}",
                duration=5
            )
            notify.popup()


    async def get_message(self, form, amount):
        contact_id = form.get('id')
        author = form.get('username')
        message = form.get('text')
        timestamp = form.get('timestamp')
        contact_username = self.storage.get_contact_username(contact_id)
        if not contact_username:
            return
        if author != contact_username:
            self.storage.update_contact_username(author, contact_id)
        if self.contact_id == contact_id and self.main.message_button_toggle:
            self.storage.message(contact_id, author, message, amount, timestamp)
        else:
            await self.handler_unread_message(contact_id, author, message, amount, timestamp)
        self.processed_timestamps.add(timestamp)


    async def handler_unread_message(self,contact_id, author, message, amount, timestamp):
        self.unread_messages_toggle = True
        self.storage.unread_message(contact_id, author, message, amount, timestamp)
        notify = NotifyGtk(
            title="New Message",
            message=f"From : {author}",
            duration=5
        )
        notify.popup()


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
        notify = NotifyGtk(
            title="New Request",
            message=f"From : {username}",
            duration=5
        )
        notify.popup()


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
                    except IndexError:
                        print(f"Skipping contact due to missing data: {data}")
                        continue
                    except Exception as e:
                        print(f"Unexpected error: {e}, data: {data}")
                        continue
            await asyncio.sleep(5)


    def add_contact_click(self, button):
        if not self.new_contact_toggle and not self.pending_toggle:
            self.new_contact = NewContact()
            self.new_contact.close_button.on_press = self.close_contact_window
            self.new_contact.show()
            self.new_contact_toggle = True


    def close_contact_window(self, button):
        self.new_contact.close()
        self.new_contact_toggle = None


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
            self.pending_list.close_button.on_press = self.close_pending_window
            self.pending_list.show()
            self.pending_toggle = True

    
    def close_pending_window(self, button):
        self.pending_list.close()
        self.pending_toggle = None


    def update_pending_list(self):
        pending = self.storage.get_pending()
        if pending:
            if not self.new_pending_toggle:
                self.pending_contacts.icon = "images/new_pending.png"
                self.new_pending_toggle = True


    def copy_messages_address(self, button):
        address = self.storage.get_identity("address")
        self.clipboard.copy(address[0])
        self.main.info_dialog(
            title="Copied",
            message="The messages address has been copied to clipboard."
        )
        


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
        await asyncio.sleep(0.2)
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
                listunspent, _= await self.commands.z_listUnspent(address[0])
                if listunspent:
                    listunspent = json.loads(listunspent)
                    list_txs = self.storage.get_txs()
                    for data in listunspent:
                        txid = data['txid']
                        if txid not in list_txs:
                            await self.unhexlify_memo(data)

                    if self.request_count > 0:
                        notify = NotifyGtk(
                            title="New Request(s)",
                            message=f"{self.request_count} New Request(s)",
                            duration=5
                        )
                        notify.popup()
                    if self.message_count > 0:
                        notify = NotifyGtk(
                            title="New Messages(s)",
                            message=f"{self.message_count} New Message(s)",
                            duration=5
                        )
                        notify.popup()

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
                timestamp = await self.get_transaction_timerecived(txid)
                if timestamp:
                    if timestamp in self.processed_timestamps:
                        highest_timestamp = max(self.processed_timestamps)
                        timestamp = highest_timestamp + 1
                    self.processed_timestamps.add(timestamp)
                    await self.get_message(form_dict, amount, timestamp)
                    self.storage.tx(txid)
                    self.message_count += 1
            elif form_type == "request":
                await self.get_request(form_dict)
                self.storage.tx(txid)
                self.request_count += 1

        except Exception as e:
            self.storage.tx(txid)
        except binascii.Error as e:
            self.storage.tx(txid)
        except json.decoder.JSONDecodeError as e:
            self.storage.tx(txid)


    async def get_message(self, form, amount, timestamp):
        id = form.get('id')
        author = form.get('username')
        message = form.get('text')
        contacts_ids = self.storage.get_contacts("contact_id")
        if id not in contacts_ids:
            return
        self.storage.unread_message(id, author, message, amount, timestamp)


    async def get_request(self, form):
        category = form.get('category')
        id = form.get('id')
        username = form.get('username')
        address = form.get('address')
        banned = self.storage.get_banned()
        if address in banned:
            return
        self.storage.add_pending(category, id, username, address)


    async def get_transaction_timerecived(self, txid):
        transaction = await self.commands.getTransaction(txid)
        json_str = transaction[0]
        data = json.loads(json_str)
        timerecived = data.get("timereceived", None)
        return timerecived
    

    def update_messages_mode(self, widget):
        mode = self.utils.get_sys_mode()
        if mode:
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
        self.chat.input_box.style.background_color = panel_color