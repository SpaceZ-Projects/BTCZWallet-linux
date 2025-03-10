
import asyncio
import aiohttp
import tarfile
import py7zr
import string
import secrets
import os
import shutil
from decimal import Decimal
import qrcode
from datetime import timedelta
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from ..framework import Gtk
from toga import App

GITHUB_API_URL = "https://api.github.com/repos/SpaceZ-Projects/BTCZWallet-linux"
RELEASES_URL = "https://github.com/SpaceZ-Projects/BTCZWallet-linux/releases"

INITIAL_REWARD = 12500
HALVING_INTERVAL = 840000


class Utils():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_data = self.app.paths.data
        self.app_cache = self.app.paths.cache
        if not os.path.exists(self.app_data):
            os.makedirs(self.app_data, exist_ok=True)
        if not os.path.exists(self.app_cache):
            os.makedirs(self.app_cache)


    def generate_id(self, length=32):
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        random_bytes = secrets.token_bytes(length)
        address_id = ''.join(alphabet[b % 62] for b in random_bytes)
        return address_id

    
    async def get_repo_info(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GITHUB_API_URL}/tags") as response:
                if response.status == 200:
                    tags = await response.json()
                    latest_tag = tags[0]['name'] if tags else None
                    if latest_tag and latest_tag.startswith("v"):
                        latest_tag = latest_tag[1:]
                    return latest_tag, RELEASES_URL
                else:
                    print(f"Failed to fetch tags: {response.status}")
                    return None, None

    def qr_generate(self, address):  
        qr_filename = f"qr_{address}.png"
        qr_path = os.path.join(self.app_cache, qr_filename)
        if os.path.exists(qr_path):
            return qr_path
        
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=7,
            border=1,
        )
        qr.add_data(address)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        with open(qr_path, 'wb') as f:
            qr_img.save(f)
        
        return qr_path

    def get_bitcoinz_path(self):
        bitcoinz_path = os.path.expanduser("~/.bitcoinz")
        return bitcoinz_path
    
    def get_zk_path(self):
        zk_params_path = os.path.expanduser("~/.zcash-params")
        return zk_params_path
    
    def get_config_path(self):
        config_file = "bitcoinz.conf"
        bitcoinz_path = self.get_bitcoinz_path()
        config_file_path = os.path.join(bitcoinz_path, config_file)
        return config_file_path
    
    def windows_screen_center(self, size):
        screen_size = self.app.screens[0].size
        screen_width, screen_height = screen_size
        window_width, window_height = size
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        return (x, y)
    
    def get_sys_mode(self):
        mode = Gtk.Settings.get_default().get_property("gtk-theme-name")
        if "dark" in mode.lower():
            return True
        return False
    
    def get_bitcoinz_size(self):
        bitcoinz_path = self.get_bitcoinz_path()
        if not os.path.exists(bitcoinz_path):
            print("Directory does not exist.")
            return 0
        total_size = 0
        for root, dirs, files in os.walk(bitcoinz_path):
            for file_name in files:
                if file_name.lower().startswith("bootstrap"):
                    continue
                file_path = os.path.join(root, file_name)
                total_size += os.path.getsize(file_path)
        total_size_gb = total_size / (1024 ** 2)
        return total_size_gb

    def generate_random_string(self, length=16):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

    def get_binary_files(self):
        required_files = [
            'bitcoinzd',
            'bitcoinz-cli',
            'bitcoinz-tx'
        ]
        missing_files = []
        for file in required_files:
            file_path = os.path.join(self.app_data, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        return missing_files
    
    def get_zk_params(self):
        zk_params_path = self.get_zk_path()
        if not os.path.exists(zk_params_path):
            os.makedirs(zk_params_path, exist_ok=True)
        required_files = [
            'sprout-proving.key',
            'sprout-verifying.key',
            'sapling-spend.params',
            'sapling-output.params',
            'sprout-groth16.params'
        ]
        missing_files = []
        for file in required_files:
            file_path = os.path.join(zk_params_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        return missing_files, zk_params_path
    

    def get_miner_path(self, miner):
        miner_folder = miner
        if miner == "MiniZ":
            miner_file = "miniZ"
            url = "https://github.com/miniZ-miner/miniZ/releases/download/v2.4e/"
            zip_file = "miniZ_v2.4e_linux-x64.tar.gz"
        elif miner == "Gminer":
            miner_file = "miner"
            url = "https://github.com/develsoftware/GMinerRelease/releases/download/3.44/"
            zip_file = "gminer_3_44_linux64.tar.xz"

        miner_dir = os.path.join(self.app_data, miner_folder)
        if not os.path.exists(miner_dir):
            os.makedirs(miner_dir)
        miner_path = os.path.join(miner_dir, miner_file)
        if os.path.exists(miner_path):
            return miner_path, url, zip_file
        return None, url, zip_file
    

    async def fetch_binary_files(self, label, progress_bar):
        file_name = "bitcoinz-c73d5cdb2b70-x86_64-linux-gnu.tar.gz"
        url = "https://github.com/btcz/bitcoinz/releases/download/2.1.0/"
        text = "Downloading binary...%"
        destination = os.path.join(self.app_data, file_name)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url + file_name, timeout=None) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        chunk_size = 512
                        downloaded_size = 0
                        self.file_handle = open(destination, 'wb')
                        async for chunk in response.content.iter_chunked(chunk_size):
                            if not chunk:
                                break
                            self.file_handle.write(chunk)
                            downloaded_size += len(chunk)
                            progress = int(downloaded_size / total_size * 100)
                            self.update_status_label(label, text, progress)
                            progress_bar.value = progress
                        self.file_handle.close()
                        self.file_handle = None
                        await session.close()
                        def extract_filter(tarinfo, fileobj):
                            return tarinfo
                        with tarfile.open(destination, 'r:gz') as tar_ref:
                            tar_ref.extractall(self.app_data, filter=extract_filter)
                        extracted_folder = os.path.join(str(self.app_data), "bitcoinz-c73d5cdb2b70")
                        bin_folder = os.path.join(extracted_folder, "bin")
                        for exe_file in ["bitcoinzd", "bitcoinz-cli", "bitcoinz-tx"]:
                            src = os.path.join(bin_folder, exe_file)
                            dest = os.path.join(str(self.app_data), exe_file)
                            if os.path.exists(src):
                                shutil.move(src, dest)
                        shutil.rmtree(extracted_folder)
                        os.remove(destination)
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def fetch_params_files(self, missing_files, zk_params_path, label, progress_bar):
        base_url = "https://d.btcz.rocks/"
        total_files = len(missing_files)
        text = "Downloading params...%"
        try:
            async with aiohttp.ClientSession() as session:
                for idx, file_name in enumerate(missing_files):
                    url = base_url + file_name
                    file_path = os.path.join(zk_params_path, file_name)
                    self.current_download_file = file_path
                    async with session.get(url, timeout=None) as response:
                        if response.status == 200:
                            total_size = int(response.headers.get('content-length', 0))
                            chunk_size = 512
                            downloaded_size = 0
                            self.file_handle = open(file_path, 'wb')
                            async for chunk in response.content.iter_chunked(chunk_size):
                                if not chunk:
                                    break
                                self.file_handle.write(chunk)
                                downloaded_size += len(chunk)
                                overall_progress = int(((idx + downloaded_size / total_size) / total_files) * 100)
                                self.update_status_label(label, text, overall_progress)
                                progress_bar.value = overall_progress
                            self.file_handle.close()
                            self.file_handle = None
                    self.current_download_file = None
                await session.close()
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def fetch_bootstrap_files(self, label, progress_bar):
        base_url = "https://github.com/btcz/bootstrap/releases/download/2024-09-04/"
        bootstrap_files = [
            'bootstrap.dat.7z.001',
            'bootstrap.dat.7z.002',
            'bootstrap.dat.7z.003',
            'bootstrap.dat.7z.004'
        ]
        total_files = len(bootstrap_files)
        bitcoinz_path = self.get_bitcoinz_path()
        text = "Downloading bootstrap...%"
        try:
            async with aiohttp.ClientSession() as session:
                for idx, file_name in enumerate(bootstrap_files):
                    file_path = os.path.join(bitcoinz_path, file_name)
                    if os.path.exists(file_path):
                        continue
                    url = base_url + file_name
                    self.current_download_file = file_path
                    async with session.get(url, timeout=None) as response:
                        if response.status == 200:
                            total_size = int(response.headers.get('content-length', 0))
                            chunk_size = 512
                            downloaded_size = 0
                            self.file_handle = open(file_path, 'wb')
                            async for chunk in response.content.iter_chunked(chunk_size):
                                if not chunk:
                                    break
                                self.file_handle.write(chunk)
                                downloaded_size += len(chunk)
                                overall_progress = int(((idx + downloaded_size / total_size) / total_files) * 100)
                                self.update_status_label(label, text, overall_progress)
                                progress_bar.value = overall_progress
                            self.file_handle.close()
                            self.file_handle = None
                    self.current_download_file = None
                await session.close()
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def fetch_miner(self, miner_selection, setup_miner_box, progress_bar, miner_folder, file_name, url):
        destination = os.path.join(self.app_data, file_name)
        miner_dir = os.path.join(self.app_data, miner_folder)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url + file_name, timeout=None) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        chunk_size = 512
                        downloaded_size = 0
                        self.file_handle = open(destination, 'wb')
                        async for chunk in response.content.iter_chunked(chunk_size):
                            if not chunk:
                                break
                            self.file_handle.write(chunk)
                            downloaded_size += len(chunk)
                            progress = int(downloaded_size / total_size * 100)
                            self.update_progress_bar(progress_bar, progress)
                        self.file_handle.close()
                        self.file_handle = None
                        await session.close()
                        await self.extract_miner(miner_selection, setup_miner_box, progress_bar, destination, miner_folder, miner_dir)
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def extract_miner(self, miner_selection, setup_miner_box, progress_bar, destination, miner_folder, miner_dir):
        if miner_folder == "MiniZ":
            miner_name = "miniZ"
            tar_extension = 'r:gz'
        elif miner_folder == "Gminer":
            miner_name = "miner"
            tar_extension = 'r:xz'
        def extract_filter(tarinfo, fileobj):
            return tarinfo
        with tarfile.open(destination, tar_extension) as tar_ref:
            tar_ref.extractall(miner_dir, filter=extract_filter)
        for root, dirs, files in os.walk(miner_dir):
            for file_name in files:
                if file_name != miner_name:
                    file_path = os.path.join(root, file_name)
                    os.remove(file_path)
        os.remove(destination)
        
        miner_selection.enabled = True
        setup_miner_box.remove(progress_bar)


    async def extract_7z_files(self):
        bitcoinz_path = self.get_bitcoinz_path()
        file_paths = [
            os.path.join(bitcoinz_path, 'bootstrap.dat.7z.001'),
            os.path.join(bitcoinz_path, 'bootstrap.dat.7z.002'),
            os.path.join(bitcoinz_path, 'bootstrap.dat.7z.003'),
            os.path.join(bitcoinz_path, 'bootstrap.dat.7z.004')
        ]
        combined_file = os.path.join(bitcoinz_path, "combined_bootstrap.7z")
        await asyncio.to_thread(self.combine_files, file_paths, combined_file)
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

        self.extract_progress_status = True
        try:
            await asyncio.to_thread(self.extract_7z, combined_file, bitcoinz_path)
            self.extract_progress_status = False
        except Exception as e:
            print(f"Error extracting file: {e}")
        os.remove(combined_file)

    def combine_files(self, file_paths, combined_file):
        with open(combined_file, 'wb') as outfile:
            for file_path in file_paths:
                with open(file_path, 'rb') as infile:
                    while chunk := infile.read(1024):
                        outfile.write(chunk)

    def extract_7z(self, combined_file, bitcoinz_path):
        with py7zr.SevenZipFile(combined_file, mode='r') as archive:
            archive.extractall(path=bitcoinz_path)

    def update_status_label(self, label, text, progress):
        if progress is None:
            label.text = text
        else:
            label.text = f"{text}{progress}"

    def update_progress_bar(self, progress_bar, progress):
        progress_bar.value = progress


    def create_config_file(self, config_file_path):
        try:
            rpcuser = self.generate_random_string(16)
            rpcpassword = self.generate_random_string(32)
            with open(config_file_path, 'w') as config_file:
                config_content = f"""# BitcoinZ configuration file
# Add your configuration settings below

rpcuser={rpcuser}
rpcpassword={rpcpassword}
addnode=178.193.205.17:1989
addnode=51.222.50.26:1989
addnode=146.59.69.245:1989
addnode=37.187.76.80:1989
"""
                config_file.write(config_content)
        except Exception as e:
            print(f"Error creating config file: {e}")


    def format_balance(self, value):
        value = Decimal(value)
        formatted_value = f"{value:.8f}"
        integer_part, decimal_part = formatted_value.split('.')
        if len(integer_part) > 4:
            digits_to_remove = len(integer_part) - 4
            formatted_decimal = decimal_part[:-digits_to_remove]
        else:
            formatted_decimal = decimal_part
        formatted_balance = f"{integer_part}.{formatted_decimal}"
        return formatted_balance
    

    def format_price(self, price):
        price = Decimal(price)

        if price > Decimal('0.00000001') and price < Decimal('0.0000001'):
            return f"{price:.10f}"
        elif price > Decimal('0.0000001') and price < Decimal('0.000001'):
            return f"{price:.9f}"
        elif price > Decimal('0.000001') and price < Decimal('0.00001'):
            return f"{price:.8f}"
        elif price > Decimal('0.00001') and price < Decimal('0.0001'):
            return f"{price:.7f}"
        elif price > Decimal('0.0001') and price < Decimal('0.001'):
            return f"{price:.6f}"
        elif price > Decimal('0.001') and price < Decimal('0.01'):
            return f"{price:.5f}"
        elif price > Decimal('0.01') and price < Decimal('0.1'):
            return f"{price:.4f}"
        elif price > Decimal('0.1') and price < Decimal('1'):
            return f"{price:.3f}"
        elif price > Decimal('1') and price < Decimal('10'):
            return f"{price:.2f}"
        elif price > Decimal('10') and price < Decimal('100'):
            return f"{price:.1f}"
        else:
            return f"{price:.0f}"
        

    def calculate_circulating(self, current_block):
        halvings = current_block // HALVING_INTERVAL
        total_supply = 0
        for i in range(halvings + 1):
            if i == halvings:
                blocks_in_period = current_block - i * HALVING_INTERVAL
            else:
                blocks_in_period = HALVING_INTERVAL
            total_supply += blocks_in_period * (INITIAL_REWARD / (2 ** i))
        return total_supply
    
    
    def remaining_blocks_until_halving(self, current_block):
        next_halving_block = (current_block // HALVING_INTERVAL + 1) * HALVING_INTERVAL
        remaining_blocks = next_halving_block - current_block
        return remaining_blocks
    

    def remaining_days_until_halving(self, current_block, block_time_minutes=2.5):
        next_halving_block = (current_block // HALVING_INTERVAL + 1) * HALVING_INTERVAL
        remaining_blocks = next_halving_block - current_block
        remaining_time_minutes = remaining_blocks * block_time_minutes
        remaining_time_delta = timedelta(minutes=remaining_time_minutes)
        remaining_days = remaining_time_delta.days
        return remaining_days
    
    def create_curve(self, data):
        mode = self.get_sys_mode()
        if mode:
            background_color = "#383838"
            text_color = "white"
        else:
            background_color = "white"
            text_color = "black"
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['formatted_price'] = df['price'].apply(lambda x: self.format_price(x))
        width, height = 2400, 600
        img = Image.new("RGB", (width, height), color=background_color)
        draw = ImageDraw.Draw(img)
        margin_left = 120
        margin_top = 50
        margin_bottom = 50
        margin_right = 50
        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom
        min_price = df['price'].min()
        max_price = df['price'].max()
        min_timestamp = df['timestamp'].min()
        max_timestamp = df['timestamp'].max()
        def scale_x(timestamp):
            return margin_left + (timestamp - min_timestamp) / (max_timestamp - min_timestamp) * plot_width
        def scale_y(price):
            return margin_top + (max_price - price) / (max_price - min_price) * plot_height
        draw.line([(margin_left, margin_top), (margin_left, height - margin_bottom)], fill="gray", width=2)
        draw.line([(margin_left, height - margin_bottom), (width - margin_right, height - margin_bottom)], fill="gray", width=2)
        for i in range(1, len(df)):
            x1 = scale_x(df['timestamp'].iloc[i-1])
            y1 = scale_y(df['price'].iloc[i-1])
            x2 = scale_x(df['timestamp'].iloc[i])
            y2 = scale_y(df['price'].iloc[i])
            draw.line([(x1, y1), (x2, y2)], fill="green", width=3)
        font = ImageFont.load_default(size=18)
        for i in range(0, len(df), len(df) // 10):
            timestamp = df['timestamp'].iloc[i]
            x = scale_x(timestamp)
            y = height - margin_bottom + 10
            draw.text((x, y), timestamp.strftime('%H:%M:%S'), font=font, fill=text_color)
        price_interval = (max_price - min_price) / 7
        for i in range(0, 8):
            price = min_price + i * price_interval
            y = scale_y(price)
            draw.text((margin_left - 100, y - 10), f"{self.format_price(price)}", font=font, fill=text_color)
        timestamp_str = df['timestamp'].iloc[0].strftime('%Y%m%d_%H%M%S')
        curve_image_path = os.path.join(self.app_cache, f'curve_{timestamp_str}.png')
        img.save(curve_image_path)

        return curve_image_path