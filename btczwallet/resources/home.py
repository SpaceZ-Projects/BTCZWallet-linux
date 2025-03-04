
import asyncio
import requests
from datetime import datetime

from toga import App, Box, Label, ImageView
from toga.style.pack import Pack
from toga.constants import (
    COLUMN, ROW, TOP, LEFT, BOLD, RIGHT,
    CENTER
)
from toga.colors import GRAY, BLACK, rgb

from .utils import Utils
from .client import Client


class Home(Box):
    def __init__(self, app:App):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                padding = (2,5,0,5),
                alignment = CENTER
            )
        )
        self.app = app
        self.utils = Utils(self.app)
        self.commands = Client(self.app)

        self.home_toggle = None
        self.cap_toggle = None
        self.volume_toggle = None
        self.curve_toggle = None

        self.market_label = Label(
            text="MarketCap :",
            style=Pack(
                font_size = 12,
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD,
                padding = (10,0,0,10)
            )
        )
        self.market_box = Box(
            style=Pack(
                direction = ROW,
                alignment = TOP,
                height = 45,
                background_color = rgb(230,230,230),
                padding = (5,5,0,5)
            )
        )

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
                color = BLACK,
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
                color = BLACK,
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
                color = BLACK,
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
                color = BLACK,
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
                font_size = 14,
                text_align = CENTER,
                color = BLACK,
                font_weight = BOLD,
                padding_top = 10
            )
        )

        self.remaining_label = Label(
            text="",
            style=Pack(
                font_size = 14,
                text_align = CENTER,
                color = BLACK,
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


    def fetch_marketcap(self):
        api_url = "https://api.coingecko.com/api/v3/coins/bitcoinz"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print("Failed to fetch data. Status code:", response.status_code)
                return None
        except Exception as e:
            print(f"Error occurred during fetch: {e}")
            return None

    def fetch_marketchart(self):
        url = "https://api.coingecko.com/api/v3/coins/bitcoinz/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': '1',
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            prices = data['prices']
            return prices
        except Exception as e:
            print(f"Error occurred during fetch: {e}")
            return None

    async def update_circulating_supply(self, widget):
        while True:
            current_block = await self.commands.getBlockCount()
            circulating = self.utils.calculate_circulating(int(current_block[0]))
            remaiming_blocks = self.utils.remaining_blocks_until_halving(int(current_block[0]))
            remaining_days = self.utils.remaining_days_until_halving(int(current_block[0]))
            self.circulating_value.text = int(circulating)
            self.halving_label.text = f"Next Halving in {remaiming_blocks} Blocks"
            self.remaining_label.text = f"Remaining {remaining_days} Days"
            await asyncio.sleep(10)


    async def update_marketcap(self, widget):
        while True:
            data = self.fetch_marketcap()
            if data:
                market_price = data["market_data"]["current_price"]["usd"]
                price_percentage_24 = data["market_data"]["price_change_percentage_24h"]
                price_percentage_7d = data["market_data"]["price_change_percentage_7d"]
                last_updated = data["market_data"]["last_updated"]

                last_updated_datetime = datetime.fromisoformat(last_updated.replace("Z", ""))
                formatted_last_updated = last_updated_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
                btcz_price = self.utils.format_price(market_price)
                self.price_value.text = f"${btcz_price}"
                self.percentage_24_value.text = f"%{price_percentage_24}"
                self.percentage_7_value.text = f"%{price_percentage_7d}"
                self.last_updated_label.text = formatted_last_updated
            await asyncio.sleep(601)

    async def update_marketchar(self, widget):
        while True:
            data = self.fetch_marketchart()
            if data:
                curve_image = self.utils.create_curve(data)
                if curve_image:
                    self.bitcoinz_curve.image = curve_image

            await asyncio.sleep(3600)