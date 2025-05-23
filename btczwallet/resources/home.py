
import asyncio
import aiohttp
from datetime import datetime
import os
import json
from aiohttp_socks import ProxyConnector, ProxyConnectionError

from toga import (
    App, Window, Box, Label, ImageView,
    Selection, Button, Divider
)
from ..framework import Gdk
from toga.style.pack import Pack
from toga.constants import (
    COLUMN, ROW, TOP, LEFT, BOLD, RIGHT,
    CENTER, Direction
)
from toga.colors import GRAY, rgb, YELLOW

from .utils import Utils
from .units import Units
from .client import Client
from .curve import Curve
from .settings import Settings



class Currency(Window):
    def __init__(self, main:Window):
        super().__init__(
            size= (200,100),
            resizable=False,
            minimizable=False,
            closable=False
        )

        self.main = main
        self.utils = Utils(self.app)
        self.settings = Settings(self.app)

        self.title = "Change Currency"
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

        self.currencies_selection = Selection(
            style=Pack(
                font_weight = BOLD,
                font_size = 12,
                padding = (20,10,10,10)
            ),
            items=[
                {"currency": ""}
            ],
            accessor="currency"
        )

        self.close_button = Button(
            text="Close",
            style=Pack(
                font_size=10,
                font_weight = BOLD,
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_currencies_window
        )

        self.content = self.main_box

        self.main_box.add(
            self.currencies_selection,
            self.close_button
        )

        self.load_currencies()

    
    def load_currencies(self):
        current_currency = self.settings.currency()
        currencies_data = self.get_currencies_list()
        self.currencies_selection.items.clear()
        for currency in currencies_data:
            self.currencies_selection.items.append(currency)
        self.currencies_selection.value = self.currencies_selection.items.find(current_currency.upper())
        self.currencies_selection.on_change = self.update_currency

    def update_currency(self, selection):
        def on_result(widget, result):
            if result is None:
                self.close()
        selected_currency = self.currencies_selection.value.currency
        if not selected_currency:
            return
        currencies_data = self.get_currencies_data()
        self.settings.update_settings("currency", selected_currency.lower())
        if selected_currency in currencies_data:
            symbol = currencies_data[selected_currency]["symbol"]
            self.settings.update_settings("symbol", symbol)
        self.info_dialog(
            title="Currency Changed",
            message="currency setting has been updated, change will take effect in a few minutes.",
            on_result=on_result
        )

    def get_currencies_data(self):
        try:
            currencies_json = os.path.join(self.app.paths.app, 'resources', 'currencies.json')
            with open(currencies_json, 'r') as f:
                currencies_data = json.load(f)
                return currencies_data
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        
    def get_currencies_list(self):
        currencies_data = self.get_currencies_data()
        if currencies_data:
            currencies_items = [{"currency": currency} for currency in currencies_data.keys()]
            return currencies_items
        
    def close_currencies_window(self, button):
        self.close()



class Home(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )
        self.app = app
        self.main = main
        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.commands = Client(self.app)
        self.curve = Curve(self.app)
        self.settings = Settings(self.app)

        self.home_toggle = None
        self.cap_toggle = None
        self.volume_toggle = None
        self.curve_image = None
        self.data = None
        self.circulating_toggle = None
        self.circulating = None

        mode = self.utils.get_sys_mode()
        if mode:
            panel_color = rgb(56,56,56)
        else:
            panel_color = rgb(230,230,230)

        self.market_label = Label(
            text="MarketCap :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD,
                padding = (10,0,0,10)
            )
        )
        self.market_box = Box(
            style=Pack(
                background_color = panel_color,
                direction = ROW,
                alignment = TOP,
                height = 45,
                padding = (5,5,0,5)
            )
        )
        self.market_box._impl.native.connect("size-allocate", self.on_box_resized)

        self.price_label = Label(
            text="Price :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.price_value = Label(
            text="",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )
        self.percentage_24_label = Label(
            "Change 24h :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.percentage_24_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )
        self.percentage_7_label = Label(
            "Change 7d :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.percentage_7_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )

        self.circulating_label = Label(
            "Circulating :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.circulating_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )
        self.circulating_value._impl.native.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.circulating_value._impl.native.set_has_window(True)
        self.circulating_value._impl.native.connect("button-press-event", self.circulating_value_click)

        self.max_emissions_value = Label(
            "21000000000",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                font_weight = BOLD
            )
        )

        self.circulating_divider = Divider(
            direction=Direction.HORIZONTAL,
            style=Pack(
                width = 100,
                flex = 1
            )
        )

        self.circulating_box = Box(
            style=Pack(
                direction = COLUMN,
                alignment = LEFT,
                flex = 1
            )
        )

        self.cap_label = Label(
            "Cap :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.cap_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )

        self.volume_label = Label(
            "Volume :",
            style=Pack(
                font_size = 11,
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD,
                padding = 10
            )
        )

        self.volume_value = Label(
            "",
            style=Pack(
                font_size = 10,
                text_align = LEFT,
                font_weight = BOLD,
                padding = (11,0,10,0),
                flex = 1
            )
        )

        self.last_updated_label = Label(
            "",
            style=Pack(
                font_size = 9,
                text_align = RIGHT,
                color = GRAY,
                font_weight = BOLD,
                padding = (5,10,0,0),
                flex = 1
            )
        )

        self.bitcoinz_curve = ImageView(
            style=Pack(
                alignment = CENTER,
                flex = 1
            )
        )

        self.halving_label = Label(
            text="",
            style=Pack(
                font_size = 12,
                text_align = CENTER,
                font_weight = BOLD,
                padding_top = 10
            )
        )

        self.remaining_label = Label(
            text="",
            style=Pack(
                font_size = 12,
                text_align = CENTER,
                font_weight = BOLD,
                padding_bottom = 10
            )
        )


    async def insert_widgets(self, widget):
        await asyncio.sleep(0.2)
        if not self.home_toggle:
            self.add(
                self.market_label, 
                self.market_box,
                self.last_updated_label,
                self.bitcoinz_curve,
                self.halving_label,
                self.remaining_label
            )
            self.market_box.add(
                self.price_label,
                self.price_value,
                self.percentage_24_label,
                self.percentage_24_value,
                self.percentage_7_label,
                self.percentage_7_value,
                self.circulating_label,
                self.circulating_box
            )
            self.circulating_box.add(
                self.circulating_value
            )

            self.home_toggle = True

            self.app.add_background_task(self.update_marketchar)
            self.app.add_background_task(self.update_marketcap)
            self.app.add_background_task(self.update_circulating_supply)


    async def fetch_marketcap(self):
        api = "https://api.coingecko.com/api/v3/coins/bitcoinz"
        tor_enabled = self.settings.tor_network()
        if tor_enabled:
            connector = ProxyConnector.from_url('socks5://127.0.0.1:9051')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                headers={'User-Agent': 'Mozilla/5.0'}
                async with session.get(api, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except ProxyConnectionError:
            return None
        except Exception as e:
            print(f"Error occurred during fetch: {e}")
            return None
        

    async def update_circulating_supply(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            current_block = await self.commands.getBlockCount()
            self.circulating = self.units.calculate_circulating(int(current_block[0]))
            remaiming_blocks = self.units.remaining_blocks_until_halving(int(current_block[0]))
            remaining_days = self.units.remaining_days_until_halving(int(current_block[0]))
            self.circulating_value.text = int(self.circulating)
            self.halving_label.text = f"Next Halving in {remaiming_blocks} Blocks"
            self.remaining_label.text = f"Remaining {remaining_days} Days"
            await asyncio.sleep(10)


    async def update_marketcap(self, widget):
        while True:
            data = await self.fetch_marketcap()
            if data:
                market_price = data["market_data"]["current_price"][self.settings.currency()]
                market_cap = data["market_data"]["market_cap"][self.settings.currency()]
                market_volume = data["market_data"]["total_volume"][self.settings.currency()]
                price_percentage_24 = data["market_data"]["price_change_percentage_24h"]
                price_percentage_7d = data["market_data"]["price_change_percentage_7d"]
                last_updated = data["market_data"]["last_updated"]

                last_updated_datetime = datetime.fromisoformat(last_updated.replace("Z", ""))
                formatted_last_updated = last_updated_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
                btcz_price = self.units.format_price(market_price)
                self.price_value.text = f"{btcz_price} {self.settings.symbol()}"
                self.percentage_24_value.text = f"{price_percentage_24} %"
                self.percentage_7_value.text = f"{price_percentage_7d} %"
                self.last_updated_label.text = formatted_last_updated
                self.cap_value.text = f"{market_cap} {self.settings.symbol()}"
                self.volume_value.text = f"{market_volume} {self.settings.symbol()}"
            await asyncio.sleep(601)
            

    async def update_marketchar(self, widget):
        while True:
            self.data = await self.curve.fetch_marketchart()
            if not self.data:
                self.main.error_dialog(
                    title="Request Error",
                    message="Too many requests. The market cap will be updated in the next 10 minutes."
                )
            else:
                curve_image = self.curve.create_curve(self.data)
                if curve_image:
                    self.bitcoinz_curve.image = curve_image
                    if self.curve_image:
                        os.remove(self.curve_image)
                    self.curve_image = curve_image

            await asyncio.sleep(602)


    def clear_cache(self):
        if self.curve_image:
            os.remove(self.curve_image)


    def on_box_resized(self, widget, allocation):
        width = allocation.width
        if not self.cap_toggle:
            if width >= 1000:
                self.market_box.add(
                    self.cap_label,
                    self.cap_value
                )
                self.cap_toggle = True
        elif self.cap_toggle:
            if width < 1000:
                self.market_box.remove(
                    self.cap_label,
                    self.cap_value
                )
                self.cap_toggle = None
        if not self.volume_toggle:
            if width >= 1200:
                self.market_box.add(
                    self.volume_label,
                    self.volume_value
                )
                self.volume_toggle = True
        elif self.volume_toggle:
            if width < 1200:
                self.market_box.remove(
                    self.volume_label,
                    self.volume_value
                )
                self.volume_toggle = None


    def circulating_value_click(self, sender, event):
        if not self.circulating_toggle:
            self.circulating_toggle = True
            self.app.add_background_task(self.show_max_emissions)


    async def show_max_emissions(self, task):
        if self.utils.get_sys_mode():
            self.max_emissions_value.style.color = YELLOW
        else:
            self.max_emissions_value.style.color = rgb(114,137,218)
        self.circulating_box.add(
            self.circulating_divider,
            self.max_emissions_value
        )
        self.circulating_value.style.padding = (2,0,2,0)
        circulating_percentage = f"{(self.circulating / 21_000_000_000) * 100:.1f}%"
        self.circulating_value._impl.native.set_tooltip_text(circulating_percentage)
        self.max_emissions_value._impl.native.set_tooltip_text(circulating_percentage)
        await asyncio.sleep(5)
        self.circulating_box.remove(
            self.circulating_divider,
            self.max_emissions_value
        )
        self.circulating_value.style.padding = (11,0,10,0)
        self.circulating_value._impl.native.set_tooltip_text("")
        self.circulating_toggle = None


    def update_home_mode(self, widget):
        if self.utils.get_sys_mode():
            panel_color = rgb(56,56,56)
        else:
            panel_color = rgb(230,230,230)
        self.market_box.style.background_color = panel_color
        curve_image = self.curve.create_curve(self.data)
        if curve_image:
            self.bitcoinz_curve.image = curve_image