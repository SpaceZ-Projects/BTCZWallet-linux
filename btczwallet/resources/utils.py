
import asyncio
import aiohttp
import tarfile
import py7zr
import os
import shutil
import qrcode
import subprocess
import shutil
from aiohttp_socks import ProxyConnector, ProxyConnectionError

from ..framework import Gtk
from toga import App

from .units import Units

GITHUB_API_URL = "https://api.github.com/repos/SpaceZ-Projects/BTCZWallet-linux"
RELEASES_URL = "https://github.com/SpaceZ-Projects/BTCZWallet-linux/releases"


class Utils():
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        self.app_path = self.app.paths.app
        self.app_data = self.app.paths.data
        self.app_cache = self.app.paths.cache
        if not os.path.exists(self.app_data):
            os.makedirs(self.app_data, exist_ok=True)
        if not os.path.exists(self.app_cache):
            os.makedirs(self.app_cache)

        self.units = Units(self.app)


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
    
    def verify_export_dir(self):
        config_file_path = self.get_config_path()
        with open(config_file_path, 'r') as config:
            lines = config.readlines()
            for line in lines:
                if line.startswith("exportdir"):
                    return True
            return None
            
    def update_config(self, path):
        config_file_path = self.get_config_path()
        updated_lines = []
        with open(config_file_path, 'r') as config:
            lines = config.readlines()
        key_found = False
        for line in lines:
            stripped_line = line.strip()
            if "=" in stripped_line:
                current_key, _ = map(str.strip, stripped_line.split('=', 1))
                if current_key == "exportdir":
                    key_found = True
                    if path is not None and path != "":
                        updated_lines.append(f"exportdir={path}\n")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        if not key_found and path is not None and path != "":
            updated_lines.append(f"exportdir={path}\n")
        with open(config_file_path, 'w') as file:
            file.writelines(updated_lines)
    
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
    

    def get_tor_files(self):
        required_files = [
            'tor_binary',
            'geoip',
            'geoip6'
        ]
        missing_files = []
        for file in required_files:
            file_path = os.path.join(self.app_data, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        return missing_files
    

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
    

    async def fetch_tor_files(self, label, progress_bar):
        file_name = "tor-expert-bundle-linux-x86_64-14.5.2.tar.gz"
        url = "https://archive.torproject.org/tor-package-archive/torbrowser/14.5.2/"
        text = "Downloading Tor bundle...%"
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
                        with tarfile.open(destination, "r:gz") as tar:
                            tar.extractall(path=self.app_data, filter=extract_filter)
                        tor_dir = os.path.join(self.app_data, "tor")
                        tor_exe = os.path.join(tor_dir, "tor")
                        dest_tor_exe = os.path.join(self.app_data, "tor_binary")
                        if os.path.exists(dest_tor_exe):
                            os.remove(dest_tor_exe)
                        shutil.move(tor_exe, dest_tor_exe)
                        data_dir = os.path.join(self.app_data, "data")
                        docs_dir = os.path.join(self.app_data, "docs")
                        debug_dir = os.path.join(self.app_data, "debug")
                        geoip_file = os.path.join(data_dir, "geoip")
                        dest_geoip = os.path.join(self.app_data, "geoip")
                        if os.path.exists(dest_geoip):
                            os.remove(dest_geoip)
                        shutil.move(geoip_file, dest_geoip)
                        geoip6_file = os.path.join(data_dir, "geoip6")
                        dest_geoip6 = os.path.join(self.app_data, "geoip6")
                        if os.path.exists(dest_geoip6):
                            os.remove(dest_geoip6)
                        shutil.move(geoip6_file, dest_geoip6)
                        for path in [tor_dir, data_dir, docs_dir, debug_dir]:
                            if os.path.isdir(path):
                                shutil.rmtree(path)
                        if os.path.exists(destination):
                            os.remove(destination)
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    

    async def fetch_binary_files(self, label, progress_bar, tor_enabled):
        file_name = "bitcoinz-c73d5cdb2b70-x86_64-linux-gnu.tar.gz"
        url = "https://github.com/btcz/bitcoinz/releases/download/2.1.0/"
        text = "Downloading binary...%"
        destination = os.path.join(self.app_data, file_name)
        if tor_enabled:
            connector = ProxyConnector.from_url('socks5://127.0.0.1:9051')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
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
        except ProxyConnectionError:
            print("Proxy connection failed.")
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def fetch_params_files(self, missing_files, zk_params_path, label, progress_bar, tor_enabled):
        base_url = "https://d.btcz.rocks/"
        total_files = len(missing_files)
        text = "Downloading params...%"
        if tor_enabled:
            connector = ProxyConnector.from_url('socks5://127.0.0.1:9051')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
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
        except ProxyConnectionError:
            print("Proxy connection failed.")
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def fetch_bootstrap_files(self, label, progress_bar, tor_enabled):
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
        if tor_enabled:
            connector = ProxyConnector.from_url('socks5://127.0.0.1:9051')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
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
        except ProxyConnectionError:
            print("Proxy connection failed.")
        except RuntimeError as e:
            print(f"RuntimeError caught: {e}")
        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


    async def fetch_miner(self, miner_selection, setup_miner_box, progress_bar, miner_folder, file_name, url, tor_enabled):
        destination = os.path.join(self.app_data, file_name)
        miner_dir = os.path.join(self.app_data, miner_folder)
        if tor_enabled:
            connector = ProxyConnector.from_url('socks5://127.0.0.1:9051')
        else:
            connector = None
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
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
        except ProxyConnectionError:
            print("Proxy connection failed.")
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
            rpcuser = self.units.generate_random_string(16)
            rpcpassword = self.units.generate_random_string(32)
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


    def add_to_startup(self):
        excutable_file = os.path.join(self.app_path.parents[3], 'bin', 'btczwallet')
        if not os.path.exists(excutable_file):
            return None
        autostart_dir = os.path.join(os.path.expanduser("~"), ".config", "autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        desktop_file = os.path.join(autostart_dir, "BTCZWallet.desktop")
        desktop_entry = f"""[Desktop Entry]
Type=Application
Name=BTCZ Wallet
Exec={excutable_file}
Icon=wallet
Terminal=false
X-GNOME-Autostart-enabled=true
"""

        try:
            with open(desktop_file, "w") as f:
                f.write(desktop_entry)
            os.chmod(desktop_file, 0o755)
            return True
        except Exception as e:
            print(f"Failed to create autostart file: {e}")
            return None
        
    
    def remove_from_startup(self):
        desktop_file = os.path.join(os.path.expanduser("~"), ".config", "autostart", "BTCZWallet.desktop")
        try:
            if os.path.exists(desktop_file):
                os.remove(desktop_file)
                return True
        except Exception as e:
            print(f"Failed to remove autostart file: {e}")
        return None
    

    def restart_app(self):
        shell_script = f"""#!/bin/bash
sleep 10
btczwallet &
rm -- "$0"
"""
        script_path = os.path.join(self.app.paths.cache, 'restart_app.sh')
        print(script_path)
        with open(script_path, 'w') as file:
            file.write(shell_script)
        
        os.chmod(script_path, 0o755)
        subprocess.Popen([str(script_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return True