# BTCZWallet-linux
BitcoinZ Full Node GUI Wallet (Linux)

# Install dependencies

- Ubuntu / Debian

```
sudo apt update
sudo apt install git build-essential pkg-config python3 python3-dev python3-venv libgirepository1.0-dev libcairo2-dev gir1.2-gtk-3.0 libcanberra-gtk3-module girepository-2.0
```
- Fedora

```
sudo dnf install git gcc make pkg-config rpm-build python3-devel gobject-introspection-devel cairo-gobject-devel gtk3 libcanberra-gtk3
```
- Arch / Manjaro

```
sudo pacman -Syu git base-devel pkgconf python3 gobject-introspection cairo gtk3 libcanberra
```

- OpenSUSE Tumbleweed

```
sudo zypper install git patterns-devel-base-devel_basis pkgconf-pkg-config python3-devel gobject-introspection-devel cairo-devel gtk3 'typelib(Gtk)=3.0' libcanberra-gtk3-module
```

# Clone the repository

```
git clone https://github.com/SpaceZ-Projects/BTCZWallet-linux.git
cd BTCZWallet-linux
python3 -m venv env
source env/bin/activate

pip install berifcase
```

# Run the Gui

```
briefcase dev
```

# Build app

```
briefcase package
``` 

