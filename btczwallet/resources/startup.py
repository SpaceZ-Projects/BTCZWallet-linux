
import asyncio
import subprocess
import json
from datetime import datetime
import os

from toga import (
    App, Box, Label, ProgressBar, Window
)
from toga.colors import rgb, GRAY, BLACK
from toga.style.pack import Pack
from toga.constants import CENTER, BOLD, COLUMN, ROW, BOTTOM, LEFT, RIGHT

from .utils import Utils
from .client import Client
from .menu import Menu


class BTCZSetup(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = COLUMN,
                flex = 1.5,
                padding = 5
            )
        )

        self.app = app
        self.main = main
        self.utils = Utils(self.app)
        self.commands = Client(self.app)
        self.app_data = self.app.paths.data

        self.node_status = None
        self.blockchaine_index = None

        self.status_label = Label(
            text="Verify binary files...",
            style=Pack(
                color = BLACK,
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                alignment = CENTER,
                padding_top = 5,
                flex = 1
            )
        )
        self.status_box = Box(
            style=Pack(
                direction=ROW,
                background_color = rgb(230,230,230),
                flex = 7
            )
        )
        self.progress_bar = ProgressBar(
            style=Pack(height= 12, flex = 1),
            max=100
        )
        self.progress_box = Box(
            style=Pack(
                direction=ROW,
                flex = 3,
                alignment = BOTTOM
            )
        )
        self.status_box.add(self.status_label)
        self.progress_box.add(self.progress_bar)
        self.add(self.status_box, self.progress_box)
        self.app.add_background_task(self.verify_binary_files)


    def update_info_box(self):
        self.status_box.remove(self.status_label)
        self.status_box.style.direction = COLUMN
        self.box1 = Box(
            style=Pack(
                direction = ROW,
                flex=1
            )
        )
        self.box2 = Box(
            style=Pack(
                direction = ROW,
                flex = 1
            )
        )
        self.blocks_txt = Label(
            text="Blocks :",
            style=Pack(
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD,
                padding_top = 3
            )
        )
        self.blocks_value = Label(
            text="",
            style=Pack(
                text_align = LEFT,
                color = BLACK,
                font_weight = BOLD,
                padding_top = 3
            )
        )
        self.mediantime_text = Label(
            text="Date :",
            style=Pack(
                text_align = LEFT,
                color = GRAY,
                font_weight = BOLD
            )
        )
        self.mediantime_value = Label(
            text="",
            style=Pack(
                text_align = LEFT,
                color = BLACK,
                font_weight = BOLD
            )
        )
        self.sync_txt = Label(
            text="Sync :",
            style=Pack(
                text_align = RIGHT,
                flex = 1,
                color = GRAY,
                font_weight = BOLD
            )
        )
        self.sync_value = Label(
            text="",
            style=Pack(
                text_align = RIGHT,
                color = BLACK,
                font_weight = BOLD
            )
        )
        self.index_size_txt = Label(
            text="Size :",
            style=Pack(
                text_align = RIGHT,
                flex = 1,
                color=GRAY,
                font_weight = BOLD,
                padding_top = 3
            )
        )
        self.index_size_value = Label(
            text="",
            style=Pack(
                text_align = RIGHT,
                color = BLACK,
                font_weight = BOLD,
                padding_top = 3
            )
        )
        self.update_status_box()
        self.update_box1()
        self.update_box2()

    def update_status_box(self):
        self.status_box.add(
            self.box1,
            self.box2
        )

    def update_box1(self):
        self.box1.add(
            self.blocks_txt,
            self.blocks_value,
            self.index_size_txt,
            self.index_size_value
        )

    def update_box2(self):
        self.box2.add(
            self.mediantime_text,
            self.mediantime_value,
            self.sync_txt,
            self.sync_value
        )

    async def verify_binary_files(self, widget):
        await asyncio.sleep(1)
        missing_files = self.utils.get_binary_files()
        if missing_files:
            text = "Downloading binary..."
            self.status_label.text = text
            await self.utils.fetch_binary_files(
                self.status_label,
                self.progress_bar
            )
        await self.verify_params_files()

    async def verify_params_files(self):
        self.status_label.text = "Verify params..."
        await asyncio.sleep(1)
        missing_files, zk_params_path = self.utils.get_zk_params()
        if missing_files:
            self.status_label.text = "Downloading params..."
            await self.utils.fetch_params_files(
                missing_files, zk_params_path,
                self.status_label, self.progress_bar,
            )
        await self.verify_config_file()


    async def verify_config_file(self):
        self.status_label.text = "Verify bitcoinz.conf..."
        await asyncio.sleep(1)
        bitcoinz_path = self.utils.get_bitcoinz_path()
        config_file_path = self.utils.get_config_path()
        if not os.path.exists(bitcoinz_path):
            self.blockchaine_index = False
            os.makedirs(bitcoinz_path, exist_ok=True)
        else:
            self.blockchaine_index = True
        if not os.path.exists(config_file_path):
            self.status_label.text = "Creating bitcoinz.conf..."
            self.utils.create_config_file(config_file_path)
            await asyncio.sleep(1)
        await self.verify_bockchaine_index()
        
    
    async def verify_bockchaine_index(self):
        if self.blockchaine_index:
            self.app.add_background_task(self.execute_bitcoinz_node)
        else:
            self.main.question_dialog(
                title="Download Bootstarp",
                message="Would you like to download the BitcoinZ bootstrap? This will help you sync faster. If you prefer to sync from block 0, Click NO.",
                on_result=self.download_bootstrap_dialog
            )

    def download_bootstrap_dialog(self, widget, result):
        if result is True:
            self.app.add_background_task(self.download_bitcoinz_bootstrap)
        elif result is False:
            self.app.add_background_task(self.execute_bitcoinz_node)


    async def download_bitcoinz_bootstrap(self, widget):
        self.status_label.text = "Downloading bootstrap..."
        await self.utils.fetch_bootstrap_files(
            self.status_label,
            self.progress_bar)
        await self.extract_bootstrap_file()


    async def extract_bootstrap_file(self):
        self.status_label.text = "Extracting bootstrap..."
        await self.utils.extract_7z_files(
            self.status_label,
            self.progress_bar
        )
        self.app.add_background_task(self.execute_bitcoinz_node)


    async def execute_bitcoinz_node(self, widget):
        self.status_label.text = "Starting node..."
        bitcoinzd = "bitcoinzd"
        node_file = os.path.join(self.app_data, bitcoinzd)
        command = [node_file]
        try:
            self.process = await asyncio.create_subprocess_exec(
                    *command,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE
            )
            await self.waiting_node_status()
        except Exception as e:
            print(e)
        finally:
            if self.process:
                await self.process.wait()
                self.process = None
                

    async def waiting_node_status(self):
        await asyncio.sleep(1)
        result, error_message = await self.commands.getInfo()
        if result:
            self.node_status = True
            await self.verify_sync_progress()
            return
        else:
            while True:
                result, error_message = await self.commands.getInfo()
                if result:
                    self.node_status = True
                    await self.verify_sync_progress()
                    return
                else:
                    if error_message:
                        self.status_label.text = error_message
                await asyncio.sleep(4)


    async def verify_sync_progress(self):
        await asyncio.sleep(1)
        blockchaininfo, _ = await self.commands.getBlockchainInfo()
        if isinstance(blockchaininfo, str):
            info = json.loads(blockchaininfo)
        if info is not None:
            sync = info.get('verificationprogress')
            sync_percentage = sync * 100
            if sync_percentage <= 99.95:
                self.update_info_box()
                self.main.info_dialog(
                    title="Disabled Wallet",
                    message="The wallet is currently disabled as it is synchronizing. It will be accessible once the sync process is complete.",
                )
                while True:
                    blockchaininfo, _ = await self.commands.getBlockchainInfo()
                    if isinstance(blockchaininfo, str):
                        info = json.loads(blockchaininfo)
                    else:
                        self.node_status = False
                        self.app.exit()
                        return
                    if info is not None:
                        blocks = info.get('blocks')
                        sync = info.get('verificationprogress')
                        mediantime = info.get('mediantime')
                    else:
                        blocks = sync = mediantime = "N/A"
                    if isinstance(mediantime, int):
                        mediantime_date = datetime.fromtimestamp(mediantime).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        mediantime_date = "N/A"
                    bitcoinz_size = self.utils.get_bitcoinz_size()
                    sync_percentage = sync * 100
                    self.blocks_value.text = f"{blocks}"
                    self.mediantime_value.text = mediantime_date
                    self.index_size_value.text = f"{int(bitcoinz_size)} MB"
                    self.sync_value.text = f"%{float(sync_percentage):.2f}"
                    self.progress_bar.value = int(sync_percentage)
                    if sync_percentage > 99.95:
                        await self.open_main_menu()
                        return
                    await asyncio.sleep(2)
            elif sync_percentage > 99.95:
                await self.open_main_menu()


    async def open_main_menu(self):
        self.main_menu = Menu()
        self.main.hide()
        await asyncio.sleep(1)
        self.main_menu.show()