
import asyncio
import operator
import json
from datetime import datetime
import webbrowser
import time

from toga import App, Box, Label, Window, Button, Table
from ..framework import Gtk, Gdk, ClipBoard, is_wsl
from toga.style.pack import Pack
from toga.colors import GRAY, GREEN, RED, ORANGE, BLACK
from toga.constants import COLUMN, CENTER, BOLD, ROW, LEFT

from .client import Client
from .utils import Utils
from .units import Units

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
        self.units = Units()
        self.commands = Client(self.app)
        self.transactions = transactions
        self.txid = txid

        self.updating_txid = None

        self.title = "Transaction Info"
        position_center = self.utils.windows_screen_center(self.size)
        self.position = position_center

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
                alignment = CENTER,
                font_weight = BOLD,
                font_size = 12,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_transaction_info
        )

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
        self.units = Units()
        self.clipboard = ClipBoard()

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
        self.transactions_table_context_menu = Gtk.Menu()
        copy_address_item = Gtk.MenuItem(label="Copy address")
        copy_address_item.connect("activate", self.copy_address)
        copy_txid_item = Gtk.MenuItem(label="Copy transaction ID")
        copy_txid_item.connect("activate", self.copy_transaction_id)
        explorer_txid_item = Gtk.MenuItem(label="View txid in explorer")
        explorer_txid_item.connect("activate", self.open_transaction_in_explorer)
        self.transactions_table_context_menu.append(copy_address_item)
        self.transactions_table_context_menu.append(copy_txid_item)
        self.transactions_table_context_menu.append(explorer_txid_item)
        self.transactions_table_context_menu.show_all()

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


    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
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
    

    def copy_address(self, centext):
        address = self.transactions_table.selection.address
        self.clipboard.copy(address)
        self.main.info_dialog(
            title="Copied",
            message="The address has copied to clipboard.",
        )

    def copy_transaction_id(self, context):
        txid = self.transactions_table.selection.txid
        self.clipboard.copy(txid)
        self.main.info_dialog(
            title="Copied",
            message="The transaction ID has copied to clipboard.",
        )

    def open_transaction_in_explorer(self, context):
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
        else:
            return


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


    async def update_transactions(self, widget):
        sorted_transactions = await self.get_transactions(
            self.transactions_count,0
        )
        if sorted_transactions:
            self.create_rows(sorted_transactions)
        while True:
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
                        try:
                            notify = NotifyGtk(
                                title=f"[{category}] : {amount} BTCZ",
                                message=f"Txid : {txid}",
                                duration=10
                            )
                            notify.popup()
                        except Exception:
                            pass
            await asyncio.sleep(5)


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
