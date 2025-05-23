
import asyncio
import json
from datetime import datetime, timezone
import ipaddress
import aiohttp
from aiohttp_socks import ProxyConnector, ProxyConnectionError, ProxyError

from toga import (
    App, Window, ScrollContainer, Box,
    Label, Divider, TextInput, Button
)
from ..framework import Gtk, Gdk, ClipBoard
from toga.constants import COLUMN, ROW, CENTER, BOLD, Direction
from toga.style.pack import Pack
from toga.colors import GRAY, BLACK, GREENYELLOW, TRANSPARENT, WHITE, RED

from .client import Client
from .utils import Utils
from .units import Units



class AddNode(Window):
    def __init__(self):
        super().__init__(
            size = (550, 120),
            resizable=False,
            closable=False
        )

        self.utils = Utils(self.app)
        self.commands = Client(self.app)

        self.title = "Add Node"
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

        self.address_input = TextInput(
            style=Pack(
                text_align= CENTER,
                font_weight = BOLD,
                font_size = 12,
                flex = 3,
                padding_left = 10
            )
        )

        self.add_button = Button(
            text="Add node",
            style=Pack(
                font_weight = BOLD,
                font_size=10,
                flex = 1,
                padding = (0,10,0,10)
            ),
            on_press=self.add_button_click
        )
        self.add_button._impl.native.connect("enter-notify-event", self.add_button_mouse_enter)
        self.add_button._impl.native.connect("leave-notify-event", self.add_button_mouse_leave)

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
                font_size=10,
                font_weight = BOLD,
                alignment = CENTER,
                padding_bottom = 10,
                width = 100
            ),
            on_press=self.close_import_key
        )
        self.cancel_button._impl.native.connect("enter-notify-event", self.cancel_button_mouse_enter)
        self.cancel_button._impl.native.connect("leave-notify-event", self.cancel_button_mouse_leave)

        self.content = self.main_box

        self.main_box.add(
            self.input_box,
            self.cancel_button
        )
        self.input_box.add(
            self.address_input,
            self.add_button
        )


    async def add_button_click(self, button):
        def on_result(widget, result):
            if result is None:
                self.close()
        node_address = self.address_input.value.strip()
        if not node_address:
            self.error_dialog(
                title="Missing Address",
                message="Please enter a node address."
            )
            return
        self.cancel_button.enabled = False
        self.add_button.enabled = False
        if 'onion' in node_address:
            connector = ProxyConnector.from_url(f'socks5://127.0.0.1:9051')
            try:
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(f"http://{node_address}", timeout=10) as response:
                        await response.text()
            except (ProxyConnectionError, ProxyError) as e:
                self.error_dialog(
                    title="Tor Proxy Error",
                    message=f"Could not connect to the .onion address : {e}"
                )
                self.cancel_button.enabled = True
                self.add_button.enabled = True
                return
            except aiohttp.ServerDisconnectedError:
                pass
        else:
            try:
                host, port = node_address.split(":")
                port = int(port)
            except ValueError:
                self.error_dialog(
                    title="Invalid Address",
                    message="Please enter a valid node address in the format IP:PORT"
                )
                self.cancel_button.enabled = True
                self.add_button.enabled = True
                return
            try:
                reader, writer = await asyncio.open_connection(host, port)
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                self.error_dialog(
                    title="Connection Failed",
                    message=f"Could not connect to the node at {node_address}."
                )
                self.cancel_button.enabled = True
                self.add_button.enabled = True
                return
        addnodes = []
        config_file_path = self.utils.get_config_path()
        with open(config_file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("addnode="):
                    addnodes.append(line.split("=", 1)[1].strip())
        if node_address in addnodes:
            self.error_dialog(
                title="Duplicate address",
                message="The node address is already exists in config file"
            )
            return
        with open(config_file_path, 'a') as file:
            file.write(f"\naddnode={node_address}")

        await self.commands.addNode(node_address)
        
        self.info_dialog(
            title="Node Added",
            message=f"Node address : {node_address} has been added to addnode list.",
            on_result=on_result
        )

            

    def add_button_mouse_enter(self, sender, event):
        self.add_button.style.color = BLACK
        self.add_button.style.background_color = GREENYELLOW

    def add_button_mouse_leave(self, widget, event):
        self.add_button.style.color = GRAY
        self.add_button.style.background_color = TRANSPARENT

    def cancel_button_mouse_enter(self, widget, event):
        self.cancel_button.style.color = WHITE
        self.cancel_button.style.background_color = RED

    def cancel_button_mouse_leave(self, widget, event):
        self.cancel_button.style.color = GRAY
        self.cancel_button.style.background_color = TRANSPARENT

    def close_import_key(self, button):
        self.close()



class Node(Box):
    def __init__(self, app:App, peer_window:Window, node):
        super().__init__(
            style=Pack(
                direction = ROW,
                height = 40,
                padding_top = 5
            )
        )
        self.app = app
        self.peer_window = peer_window

        self.utils = Utils(self.app)
        self.units = Units(self.app)
        self.commands = Client(self.app)
        self.clipboard = ClipBoard()

        self.address = node.get('addr')
        self.address_local = node.get('addrlocal')
        address = self.shorten_address(self.address)
        address_local = self.shorten_address(self.address_local)
        bytessent = node.get('bytessent')
        bytesrecv = node.get('bytesrecv')
        subver = node.get('subver')
        clean_subversion = subver.strip('/')
        conntime = node.get('conntime')
        conn_time = datetime.fromtimestamp(conntime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        duration = now - conn_time
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if days > 0:
            conn_duration_str = f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            conn_duration_str = f"{hours}h {minutes}m"
        else:
            conn_duration_str = f"{minutes}m"


        self.node_address = Label(
            text=address,
            style=Pack(
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_address._impl.native.set_tooltip_text(self.address_local)

        self.node_address_local = Label(
            text=address_local,
            style=Pack(
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_sent = Label(
            text=self.units.format_bytes(bytessent),
            style=Pack(
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_receive = Label(
            text=self.units.format_bytes(bytesrecv),
            style=Pack(
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.node_subversion = Label(
            text=clean_subversion,
            style=Pack(
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.node_conntime= Label(
            text=conn_duration_str,
            style=Pack(
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.add(
            self.node_address,
            self.node_address_local,
            self.node_sent,
            self.node_receive,
            self.node_subversion,
            self.node_conntime
        )
        self.node_address._impl.native.set_has_window(True)
        self.node_address._impl.native.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.node_address_local._impl.native.set_has_window(True)
        self.node_address_local._impl.native.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.node_sent._impl.native.set_has_window(True)
        self.node_sent._impl.native.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.node_receive._impl.native.set_has_window(True)
        self.node_receive._impl.native.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.node_subversion._impl.native.set_has_window(True)
        self.node_subversion._impl.native.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        self._impl.native.connect("button-press-event", self.node_context_event)
        self.node_address._impl.native.connect("button-press-event", self.node_context_event)
        self.node_address_local._impl.native.connect("button-press-event", self.node_context_event)
        self.node_sent._impl.native.connect("button-press-event", self.node_context_event)
        self.node_receive._impl.native.connect("button-press-event", self.node_context_event)
        self.node_subversion._impl.native.connect("button-press-event", self.node_context_event)
        self.node_context_menu = Gtk.Menu()
        copy_address_item = Gtk.MenuItem(label="Copy node address")
        copy_address_item.connect("activate", self.copy_node_address)
        remove_node_item = Gtk.MenuItem(label="Remove node")
        remove_node_item.connect("activate", self.remove_node_from_config)
        self.node_context_menu.append(copy_address_item)
        self.node_context_menu.append(remove_node_item)
        self.node_context_menu.show_all()


    def node_context_event(self, widget, event):
        if event.button == Gdk.BUTTON_SECONDARY:
            self.node_context_menu.popup_at_pointer(event)
            return True
        return False
    

    def copy_node_address(self, event):
        self.clipboard.copy(self.address)
        self.peer_window.info_dialog(
            title="Copied",
            message="The node address has copied to clipboard.",
        )


    def remove_node_from_config(self, event):
        config_file_path = self.utils.get_config_path()
        with open(config_file_path, 'r') as file:
            lines = file.readlines()
        update_lines = []
        for line in lines:
            if line.startswith('addnode='):
                _, value = line.split('=', 1)
                value = value.strip()
                if value != self.address:
                    update_lines.append(line)
            else:
                update_lines.append(line)
        with open(config_file_path, 'w') as file:
            file.writelines(update_lines)
        self.app.add_background_task(self.remove_node)
        
    
    async def remove_node(self, widget):
        await self.commands.disconnectNode(self.address)
        await self.commands.removeNode(self.address)
        self.peer_window.info_dialog(
            title="Node Removed",
            message=f"Node address : {self.address} has been removed form addnode list"
        )



    @staticmethod
    def is_ipv6_address(address: str) -> bool:
        try:
            if address.startswith("[") and "]" in address:
                address = address[1:].split("]")[0]
            ipaddress.IPv6Address(address)
            return True
        except ValueError:
            return False
    

    def shorten_address(self, address: str) -> str:
        if not address:
            return "N/A"
        if '.onion' in address:
            return address[:12] + "...onion"
        elif self.is_ipv6_address(address):
            return address[:8] + "...IPv6"
        else:
            return address


class Peer(Window):
    def __init__(self, main:Window):
        super().__init__()

        self.main = main
        self.commands = Client(self.app)
        self.units = Units(self.app)

        self.title = "Peer Info"
        self.size = self.main.size
        self.position = self.main.position
        self.on_close = self.close_peers_window

        self.peers_list = []
        self.node_map = {}

        self.main_scroll = ScrollContainer(
            style=Pack(
                flex = 1
            )
        )

        self.scroll_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )

        self.main_box = Box(
            style=Pack(
                direction = COLUMN,
                flex = 1,
                alignment = CENTER
            )
        )

        self.titles_box = Box(
            style=Pack(
                direction = ROW,
                height = 40
            )
        )
        self.address_title = Label(
            text="Address",
            style=Pack(
                color = GRAY,
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.address_local_title = Label(
            text="Address local",
            style=Pack(
                color = GRAY,
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.sent_title = Label(
            text="Sent",
            style=Pack(
                color = GRAY,
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.receive_title = Label(
            text="Received",
            style=Pack(
                color = GRAY,
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.subversion_title = Label(
            text="Subversion",
            style=Pack(
                color = GRAY,
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )

        self.conntime_title = Label(
            text="Conn. Time",
            style=Pack(
                color = GRAY,
                font_size = 10,
                font_weight = BOLD,
                text_align = CENTER,
                flex = 1,
                padding_top = 10
            )
        )
        self.main_scroll.content = self.main_box
        self.scroll_box.add(
            self.main_scroll
        )

        self.main_box.add(
            self.titles_box
        )
        self.titles_box.add(
            self.address_title,
            self.address_local_title,
            self.sent_title,
            self.receive_title,
            self.subversion_title,
            self.conntime_title
        )
        self.content = self.scroll_box

        self.app.add_background_task(self.get_peers_info)


    async def get_peers_info(self, widget):
        while True:
            if not self.main.peer_toggle:
                return
            if self.main.import_key_toggle:
                self.main.peer_toggle = None
                self.close()
                return

            peerinfo, _ = await self.commands.getPeerinfo()
            if peerinfo:
                peerinfo = json.loads(peerinfo)
                current_addresses = set()
                node_by_address = {}

                for node in peerinfo:
                    address = node.get('addr')
                    current_addresses.add(address)
                    node_by_address[address] = node

                    if address not in self.peers_list:
                        self.peers_list.append(address)
                        self.add_peer(node)

                for address in list(self.peers_list):
                    if address not in current_addresses:
                        self.remove_peer({'addr': address})
                        self.peers_list.remove(address)
                    else:
                        self.update_peer(node_by_address[address])

                current_addresses.clear()

            await asyncio.sleep(5)


    def add_peer(self, node):
        node_box = Node(self.app, self, node)
        box_divider = Divider(
            direction=Direction.HORIZONTAL,
            style=Pack(
                background_color = WHITE,
                flex =1
            )
        )
        self.main_box.add(node_box, box_divider)
        self.node_map[node.get('addr')] = (node_box, box_divider)

    
    def update_peer(self, node):
        address = node.get('addr')
        widgets = self.node_map.get(address)
        if not widgets:
            return
        node_box, _ = widgets
        lastsend = node.get('lastsend')
        lastrecv = node.get('lastrecv')
        conntime = node.get('conntime')
        conn_time = datetime.fromtimestamp(conntime, tz=timezone.utc)
        last_send = datetime.fromtimestamp(lastsend).strftime('%Y-%m-%d %H:%M:%S')
        last_receive = datetime.fromtimestamp(lastrecv).strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.now(timezone.utc)
        duration = now - conn_time
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        if days > 0:
            conn_duration = f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            conn_duration = f"{hours}h {minutes}m"
        else:
            conn_duration = f"{minutes}m"
        node_box.node_sent.text = self.units.format_bytes(node.get('bytessent'))
        node_box.node_sent._impl.native.set_tooltip_text(f"Last send :{last_send}")
        node_box.node_receive.text = self.units.format_bytes(node.get('bytesrecv'))
        node_box.node_receive._impl.native.set_tooltip_text(f"Last receive :{last_receive}")
        node_box.node_conntime.text = conn_duration


    def remove_peer(self, node):
        address = node.get('addr')
        widgets = self.node_map.get(address)
        if widgets:
            node_box, box_divider = widgets
            self.main_box.remove(node_box)
            self.main_box.remove(box_divider)
            del self.node_map[address]


    def close_peers_window(self, widget):
        self.main.peer_toggle = None
        self.close()