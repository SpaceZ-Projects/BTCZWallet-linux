
import asyncio
import json
import binascii

from toga import (
    App, Box, Window, Button, Label, TextInput,
    ScrollContainer
)
from ..framework import ClipBoard
from toga.style.pack import Pack
from toga.constants import ROW, CENTER, COLUMN, BOLD
from toga.colors import rgb, BLACK, GRAY

from .storage import Storage
from .utils import Utils
from .client import Client



class Indentifier(Window):
    def __init__(self, messages_page:Box, main:Window, chat:Box):
        super().__init__(
            size = (700, 150),
            resizable= False,
            minimizable = False,
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

        self.add_contact = Button(
            icon="images/add_contact"
        )
        self.add_contact._impl.native.set_tooltip_text("Add new contact")

        self.pending_contacts = Button(
            icon="images/pending"
        )
        self.pending_contacts._impl.native.set_tooltip_text("Show pending contacts")

        self.copy_address = Button(
            icon="images/copy.png",
            on_press=self.copy_messages_address
        )
        self.copy_address._impl.native.set_tooltip_text("Copy your messages address")

        self.buttons_box = Box(
            style=Pack(
                alignment = CENTER,
                direction = ROW,
                background_color = rgb(230,230,230),
                height = 42
            )
        )

        self.address_balance = Label(
            text = f"Balance : 0.00000000",
            style=Pack(
                color = rgb(114,137,218),
                background_color = rgb(230,230,230),
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
                background_color = rgb(230,230,230),
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

    
    def run_tasks(self):
        self.app.add_background_task(self.update_messages_balance)


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
                        print(f"{self.request_count} New Request(s)")
                    if self.message_count > 0:
                        print(f"{self.message_count} New Message(s)")

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