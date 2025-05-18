
import asyncio
from datetime import datetime
import json

from toga import App, Window, Box
from ..framework import StatusBar
from toga.style.pack import Pack
from toga.constants import ROW, BOTTOM

from .client import Client
from .utils import Utils


class AppStatusBar(Box):
    def __init__(self, app:App, main:Window):
        super().__init__(
            style=Pack(
                direction = ROW,
                alignment = BOTTOM,
                height = 24
            )
        )
        self.app = app
        self.main = main
        self.commands = Client(self.app)
        self.utils = Utils(self.app)

        self.statusbar = StatusBar()
        self._impl.native.pack_start(self.statusbar, True, True, 0)

        self.app.add_background_task(self.update_status_bar)


    async def update_status_bar(self, widget):
        while True:
            if self.main.import_key_toggle:
                await asyncio.sleep(1)
                continue
            blockchaininfo, _ = await self.commands.getBlockchainInfo()
            networksol, _ = await self.commands.getNetworkSolps()
            connection_count,_ = await self.commands.getConnectionCount()
            deprecationinfo, _ = await self.commands.getDeprecationInfo()
            if blockchaininfo is not None:
                if isinstance(blockchaininfo, str):
                    info = json.loads(blockchaininfo)
                if info is not None:
                    blocks = info.get('blocks')
                    sync = info.get('verificationprogress')
                    mediantime = info.get('mediantime')
                else:
                    blocks = sync = mediantime = "N/A"
            else:
                blocks = sync = mediantime = "N/A"
            if isinstance(mediantime, int):
                mediantime_date = datetime.fromtimestamp(mediantime).strftime('%Y-%m-%d %H:%M:%S')
            else:
                mediantime_date = "N/A"
            bitcoinz_size = self.utils.get_bitcoinz_size()
            sync_percentage = sync * 100
            if networksol is not None:
                if isinstance(networksol, str):
                    info = json.loads(networksol)
                if info is not None:
                    netsol = info
                else:
                    netsol = "N/A"
            if deprecationinfo is not None:
                if isinstance(deprecationinfo, str):
                    info = json.loads(deprecationinfo)
                if info is not None:
                    deprecation = info.get('deprecationheight')
                else:
                    deprecation = "N/A"

            status_text = f"Blocks : {blocks} | Date : {mediantime_date} | Sync : {float(sync_percentage):.2f}% | NetHash : {netsol} Sol/s | Conns : {connection_count} | Dep : {deprecation} | Size : {int(bitcoinz_size)} MB"
            self.statusbar.add(status_text)

            await asyncio.sleep(5)