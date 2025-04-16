
import asyncio
import aiohttp
from datetime import datetime
import os

from toga import App, Window, Box, Label, ImageView
from toga.style.pack import Pack
from toga.constants import (
    COLUMN, ROW, TOP, LEFT, BOLD, RIGHT,
    CENTER
)
from toga.colors import GRAY, rgb

from .utils import Utils
from .units import Units
from .client import Client
from .curve import Curve


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

        self.home_toggle = None
        self.cap_toggle = None
        self.volume_toggle = None
        self.curve_image = None
        self.data = None

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
                self.circulating_value
            )

            self.home_toggle = True

            self.app.add_background_task(self.update_marketchar)
            self.app.add_background_task(self.update_marketcap)
            self.app.add_background_task(self.update_circulating_supply)


    async def fetch_marketcap(self):
        api = "https://api.coingecko.com/api/v3/coins/bitcoinz"
        try:
            async with aiohttp.ClientSession() as session:
                headers={'User-Agent': 'Mozilla/5.0'}
                async with session.get(api, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except Exception as e:
            print(f"Error occurred during fetch: {e}")
            return None
        

    async def update_circulating_supply(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            current_block = await self.commands.getBlockCount()
            circulating = self.units.calculate_circulating(int(current_block[0]))
            remaiming_blocks = self.units.remaining_blocks_until_halving(int(current_block[0]))
            remaining_days = self.units.remaining_days_until_halving(int(current_block[0]))
            self.circulating_value.text = int(circulating)
            self.halving_label.text = f"Next Halving in {remaiming_blocks} Blocks"
            self.remaining_label.text = f"Remaining {remaining_days} Days"
            await asyncio.sleep(10)


    async def update_marketcap(self, widget):
        while True:
            data = await self.fetch_marketcap()
            if data:
                market_price = data["market_data"]["current_price"]["usd"]
                market_cap = data["market_data"]["market_cap"]["usd"]
                market_volume = data["market_data"]["total_volume"]["usd"]
                price_percentage_24 = data["market_data"]["price_change_percentage_24h"]
                price_percentage_7d = data["market_data"]["price_change_percentage_7d"]
                last_updated = data["market_data"]["last_updated"]

                last_updated_datetime = datetime.fromisoformat(last_updated.replace("Z", ""))
                formatted_last_updated = last_updated_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
                btcz_price = self.units.format_price(market_price)
                self.price_value.text = f"${btcz_price}"
                self.percentage_24_value.text = f"%{price_percentage_24}"
                self.percentage_7_value.text = f"%{price_percentage_7d}"
                self.last_updated_label.text = formatted_last_updated
                self.cap_value.text = f"${market_cap}"
                self.volume_value.text = f"${market_volume}"
            await asyncio.sleep(601)
            

    async def update_marketchar(self, widget):
        while True:
            self.data = await self.curve.fetch_marketchart()
            if self.data:
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


    def update_home_mode(self, widget):
        mode = self.utils.get_sys_mode()
        if mode:
            panel_color = rgb(56,56,56)
        else:
            panel_color = rgb(230,230,230)
        self.market_box.style.background_color = panel_color
        curve_image = self.curve.create_curve(self.data)
        if curve_image:
            self.bitcoinz_curve.image = curve_image