
import asyncio
import operator
import json
from datetime import datetime
import webbrowser
import time
from functools import partial

from toga import App, Box, Label, Window, Button, Table
from ..framework import Gdk, ClipBoard, is_wsl, Menu, Command
from toga.style.pack import Pack
from toga.colors import GRAY, GREEN, RED, ORANGE, BLACK, WHITE, TRANSPARENT
from toga.constants import COLUMN, CENTER, BOLD, ROW, LEFT

from .client import Client
from .utils import Utils
from .units import Units
from .settings import Settings

if not is_wsl():
    from ..framework import NotifyGtk


class Txid(Window):
    def __init__(self, transactions, txid):
        super().__init__(
            size =(700, 150),
            resizable= False,
            closable=False,
            on_close=self.close_transaction_info
        )

        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.commands = Client(self.app)
        self.transactions = transactions
        self.txid = txid

        self.updating_txid = None

        self.title = "Transaction Info"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

        self._impl.native.set_keep_above(True)
        self._impl.native.set_modal(True)

        self.main_box = Box(
            style=Pack(
                alignment = CENTER,
                direction = COLUMN,
                flex = 1
            )
        )

        self.txid_label = Label(
            text="Transaction ID : ",
            style=Pack(
                font_weight = BOLD,
                text_align = CENTER,
                color = GRAY,
                padding_left = 10
            )
        )
        self.txid_value = Label(
            text=self.txid,
            style=Pack(
                font_weight = BOLD,
                text_align = CENTER
            )
        )
        self.txid_box = Box(
            style=Pack(
                direction = ROW,
                flex = 2,
                alignment = CENTER
            )
        )

        self.confirmations_label = Label(
            text="Confirmations : ",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                color = GRAY,
                padding_left = 50
            )
        )
        self.confirmations_value = Label(
            text="",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                flex = 1
            )
        )
        self.confirmations_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                alignment = LEFT
            )
        )

        self.category_label = Label(
            text="Category : ",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                color = GRAY,
                padding_left = 50
            )
        )
        self.category_value = Label(
            text="",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                flex = 1
            )
        )
        self.category_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                alignment = LEFT
            )
        )

        self.amount_label = Label(
            text="Amount : ",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                color = GRAY,
                padding_left = 50
            )
        )
        self.amount_value = Label(
            text="",
            style=Pack(
                font_weight = BOLD,
                text_align = LEFT,
                flex = 1
            )
        )
        self.amount_box = Box(
            style=Pack(
                direction = ROW,
                flex = 1,
                alignment = LEFT
            )
        )
        
        self.close_button = Button(
            text="Close",
            style=Pack(
                color=GRAY,
                alignment = CENTER,
                font_weight = BOLD,
                font_size = 12,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_transaction_info
        )
        self.close_button._impl.native.connect("enter-notify-event", self.close_button_mouse_enter)
        self.close_button._impl.native.connect("leave-notify-event", self.close_button_mouse_leave)

        self.content = self.main_box

        self.main_box.add(
            self.txid_box,
            self.confirmations_box,
            self.category_box,
            self.amount_box,
            self.close_button
        )
        self.txid_box.add(
            self.txid_label,
            self.txid_value
        )
        self.confirmations_box.add(
            self.confirmations_label,
            self.confirmations_value
        )
        self.category_box.add(
            self.category_label,
            self.category_value
        )
        self.amount_box.add(
            self.amount_label,
            self.amount_value
        )

        self.app.add_background_task(self.update_transaction_info)


    async def update_transaction_info(self, widget):
        if not self.updating_txid:
            self.updating_txid = True
            while True:
                if not self.updating_txid:
                    return
                transaction_info, _= await self.commands.getTransaction(self.txid)
                if isinstance(transaction_info, str):
                    transaction_info = json.loads(transaction_info)
                if transaction_info:
                    category = transaction_info['details'][0]['category']
                    amount = self.units.format_balance(float(transaction_info['amount']))
                    confirmations = transaction_info['confirmations']
                    if confirmations <= 0:
                        color = RED
                    elif 1 <= confirmations < 6:
                        color = ORANGE
                    else:
                        color = GREEN
                    self.confirmations_value.style.color = color
                    self.confirmations_value.text = confirmations
                    self.category_value.text = category
                    self.amount_value.text = amount
                
                await asyncio.sleep(5)

    
    def close_button_mouse_enter(self, sender, event):
        self.close_button.style.color = WHITE
        self.close_button.style.background_color = RED

    def close_button_mouse_leave(self, sender, event):
        self.close_button.style.color = GRAY
        self.close_button.style.background_color = TRANSPARENT


    def close_transaction_info(self, button):
        self.updating_txid = None
        self.transactions.transaction_info_toggle = None
        self.close()



class Transactions(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                padding = (1,5,0,5)
            )
        )

        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.clipboard = ClipBoard()
        self.settings = Settings(self.app)

        self.transactions_toggle = None
        self.no_transaction_toggle = None
        self.transactions_data = []
        self.last_click_time = 0
        self.double_click_threshold = 0.5
        self.double_click_handler = None
        self.transaction_info_toggle = None

        self.transactions_count = 49
        self.transactions_from = 0

        self.transactions_table = Table(
            headings=["Category", "Address", "Amount", "Time", "Txid"],
            accessors=["category", "address", "amount", "time", "txid"],
            style=Pack(
                flex = 1,
                color = BLACK,
                font_weight = BOLD
            )
        )
        transactions_table_widgets = self.transactions_table._impl.native.get_child()
        v_adjustment = transactions_table_widgets.get_vadjustment()
        v_adjustment.connect("value-changed", self.on_scroll_table)
        transactions_table_widgets.connect("button-press-event", self.transactions_table_context_event)

        self.transactions_table_context_menu = Menu()
        self.copy_address_cmd = Command(
            title="Copy address",
            action=self.copy_address,
        )
        self.copy_txid_cmd = Command(
            title="Copy transaction ID",
            action=self.copy_transaction_id
        )
        self.explorer_txid_cmd = Command(
            title="View txid in explorer",
            action=self.open_transaction_in_explorer
        )
        self.transactions_table_context_menu.add_commands(
            [
                self.copy_address_cmd,
                self.copy_txid_cmd,
                self.explorer_txid_cmd
            ]
        )

        self.no_transaction = Label(
            text="No Transactions found.",
            style=Pack(
                color = BLACK,
                text_align = CENTER,
                font_weight = BOLD,
                font_size = 14,
                padding_top = 40
            )
        )
        self.set_transactions_context_icons()


    def set_transactions_context_icons(self):
        if self.utils.get_sys_mode():
            self.copy_address_cmd.icon = "images/copy_w.png"
            self.copy_txid_cmd.icon = "images/copy_w.png"
            self.explorer_txid_cmd.icon = "images/explorer_w.png"
        else:
            self.copy_address_cmd.icon = "images/copy_b.png"
            self.copy_txid_cmd.icon = "images/copy_b.png"
            self.explorer_txid_cmd.icon = "images/explorer_b.png"
        


    async def insert_widgets(self, widget):
        if not self.transactions_toggle:
            if self.transactions_data:
                self.add(self.transactions_table)
                self.transactions_table.data = self.transactions_data
            else:
                await self.no_transactions_found()
            self.transactions_toggle = True


    def transactions_table_context_event(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            current_time = time.time()
            if current_time - self.last_click_time <= self.double_click_threshold and not self.double_click_handler:
                self.transactions_table_double_click(widget, event)
                self.double_click_handler = True
            else:
                self.double_click_handler = False
            self.last_click_time = current_time
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.transactions_table_context_menu.popup_at_pointer(event)
            return True
        return False
    

    def copy_address(self, action):
        address = self.transactions_table.selection.address
        self.clipboard.copy(address)
        self.main.info_dialog(
            title="Copied",
            message="The address has copied to clipboard.",
        )

    def copy_transaction_id(self, action):
        txid = self.transactions_table.selection.txid
        self.clipboard.copy(txid)
        self.main.info_dialog(
            title="Copied",
            message="The transaction ID has copied to clipboard.",
        )

    def open_transaction_in_explorer(self, action):
        url = "https://explorer.btcz.rocks/tx/"
        txid = self.transactions_table.selection.txid
        transaction_url = url + txid
        webbrowser.open(transaction_url)


    def on_scroll_table(self, adjustment):
        vertical_position = adjustment.get_value()
        max_value = adjustment.get_upper() - adjustment.get_page_size()
        if vertical_position >= max_value:
            self.transactions_from += 50
            self.app.add_background_task(self.get_transactions_archive)


    def transactions_table_double_click(self, widget, event):
        if not self.transaction_info_toggle:
            txid = self.transactions_table.selection.txid
            self.transaction_info = Txid(self, txid)
            self.transaction_info.show()
            self.double_click_handler = False
            self.transaction_info_toggle = True


    def create_rows(self, sorted_transactions):
        for data in sorted_transactions:
            address = data.get("address", "Shielded")
            category = data["category"]
            amount = self.units.format_balance(data["amount"])
            timereceived = data["timereceived"]
            formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
            txid = data["txid"]
            row = {
                "category": category.upper(),
                "address": address,
                "amount": amount,
                "time": formatted_timereceived,
                "txid": txid
            }
            self.transactions_data.append(row)


    async def no_transactions_found(self):
        self.add(self.no_transaction)
        self.no_transaction_toggle = True


    async def reload_transactions(self):
        if self.transactions_data:
            self.transactions_data.clear()
        sorted_transactions = await self.get_transactions(
            self.transactions_count,0
        )
        if sorted_transactions:
            self.create_rows(sorted_transactions)
            if self.no_transaction_toggle:
                self.remove(self.no_transaction)
                self.add(self.transactions_table)
            else:
                if self.transactions_toggle:
                    self.transactions_table.data = self.transactions_data


    async def update_transactions(self, widget):
        sorted_transactions = await self.get_transactions(
            self.transactions_count,0
        )
        if sorted_transactions:
            self.create_rows(sorted_transactions)
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            new_transactions = await self.get_transactions(self.transactions_count,0)
            if new_transactions:
                for data in new_transactions:
                    txid = data["txid"]
                    if not any(tx["txid"] == txid for tx in self.transactions_data):
                        address = data.get("address", "Shielded")
                        category = data["category"]
                        amount = self.units.format_balance(data["amount"])
                        timereceived = data["timereceived"]
                        formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                        row = {
                            "category": category.upper(),
                            "address": address,
                            "amount": amount,
                            "time": formatted_timereceived,
                            "txid": txid
                        }
                        self.transactions_data.insert(0, row)
                        self.add_transaction(0, row)
                        if self.settings.notification_txs():
                            try:
                                notify = NotifyGtk(
                                    title=f"[{category}] : {amount} BTCZ",
                                    message=f"Txid : {txid}",
                                    duration=10,
                                    on_press=partial(self.on_notification_click, txid)
                                )
                                notify.popup()
                            except Exception:
                                pass
            await asyncio.sleep(5)

    
    def on_notification_click(self, txid):
        if not self.transaction_info_toggle:
            self.transaction_info = Txid(self, txid)
            self.transaction_info.show()
            self.transaction_info_toggle = True


    def add_transaction(self, index, row):
        if self.no_transaction_toggle:
            self.remove(self.no_transaction)
            self.add(self.transactions_table)
            self.transactions_table.data = self.transactions_data
            self.no_transaction_toggle = None
        else:
            if self.transactions_toggle and not self.no_transaction_toggle:
                self.transactions_table.data.insert(index=index, data=row)
                

    async def get_transactions(self, count, tx_from):
        transactions, _ = await self.commands.listTransactions(
            count, tx_from
        )
        if isinstance(transactions, str):
            transactions_data = json.loads(transactions)
        if transactions_data:
            sorted_transactions = sorted(
                transactions_data,
                key=operator.itemgetter('timereceived'),
                reverse=True
            )
            return sorted_transactions
        return None


    async def get_transactions_archive(self, widget):
        sorted_transactions = await self.get_transactions(
            self.transactions_count, self.transactions_from
        )
        if sorted_transactions:
            for data in sorted_transactions:
                address = data.get("address", "Shielded")
                category = data["category"]
                amount = self.units.format_balance(data["amount"])
                timereceived = data["timereceived"]
                formatted_timereceived = datetime.fromtimestamp(timereceived).strftime("%Y-%m-%d %H:%M:%S")
                txid = data["txid"]
                row = {
                    'Category': category.upper(),
                    'Address': address,
                    'Amount': amount,
                    'Time': formatted_timereceived,
                    'Txid': txid,
                }
                last_index = len(self.transactions_table.data)
                self.add_transaction(last_index, row)
    

    def update_transactions_mode(self, widget):
        self.set_transactions_context_icons()