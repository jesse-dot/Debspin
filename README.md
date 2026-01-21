# Debspin - Debian Spinoff Creator

Debspin is an easy-to-use GUI application for creating custom Debian-based Linux distributions (spinoffs) as bootable ISO files.

## Features

- **Custom OS Name**: Specify the name of your custom Debian distribution
- **Version Code**: Set your own version code for the ISO (e.g., "1.0", "2024.1")
- **Desktop Environment Selection**: Choose from popular desktop managers including:
  - KDE Plasma (default)
  - GNOME
  - XFCE
  - LXDE
  - Cinnamon
  - MATE
  - Budgie
  - i3
  - None (Server/Minimal)
- **Package Selection**: Add custom packages to be included in your spinoff
- **ISO Generation**: Build bootable ISO files with:
  - Live boot capability (try before installing)
  - Installation capability (install to hard drive)
  - User-selected desktop environment pre-configured
  - Custom package selection included

## Requirements

- Python 3.x
- tkinter (usually included with Python)

### Installing tkinter

If tkinter is not available on your system, install it using your package manager:

- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **Arch Linux**: `sudo pacman -S tk`

### Optional: Full ISO Building Tools

For creating fully bootable ISOs (recommended for production use), install these additional tools:

- **Ubuntu/Debian**: `sudo apt-get install debootstrap xorriso squashfs-tools`
- **Fedora**: `sudo dnf install debootstrap xorriso squashfs-tools`
- **Arch Linux**: `sudo pacman -S debootstrap libisoburn squashfs-tools`

**Important**: Building a full bootable ISO requires **root/sudo privileges** because debootstrap needs to perform chroot operations and mount filesystems.

**Note**: Without these tools or root privileges, Debspin will create a demonstration ISO with all metadata and configuration files, but it won't be fully bootable. The demonstration ISO still contains all the necessary configuration to show what would be included in a full build.

## Usage

### Method 1: Using the launcher script (for full ISO building)

```bash
sudo ./launch_debspin.sh
```

### Method 2: Direct Python execution (for full ISO building)

```bash
sudo python3 debspin_gui.py
```

### Method 3: Without sudo (creates demonstration ISO only)

```bash
python3 debspin_gui.py
```

## How to Use

1. **Enter OS Name**: Type the name of your custom Debian distribution (e.g., "MyDebianSpin")
2. **Enter Version Code**: Specify the version (e.g., "1.0", "2024.1")
3. **Select Desktop Manager**: Choose from the dropdown menu (defaults to KDE Plasma)
4. **Add Packages**: Enter package names, one per line, in the text area
5. **Preview Configuration**: Click "Preview Configuration" to see your settings in JSON format
6. **Build ISO**: Click "Build ISO" to create your custom Debian ISO file

The ISO will be named: `{os_name}-{version_code}.iso`

## ISO File Format

The generated ISO contains:

- **Bootable configuration** with GRUB boot menu
- **Live boot option** to try the system without installing
- **Installation option** to install to hard drive
- **Desktop environment** packages for your selected DE
- **Custom packages** you specified
- **Metadata** describing the ISO contents

### Example ISO Contents

```
iso/
├── README.txt              # Information about the ISO
├── debspin_metadata.json   # ISO metadata and configuration
├── packages.list           # List of all included packages
└── boot/
    └── grub.cfg           # Boot configuration
```

### Metadata Format

```json
{
  "iso_type": "Debian Custom Spinoff",
  "name": "MyDebianSpin",
  "version": "1.0",
  "desktop_manager": "KDE Plasma",
  "packages": ["firefox-esr", "libreoffice", "vlc"],
  "bootable": true,
  "live_boot": true,
  "installation_capable": true
}
```

## Example Workflow

1. Launch the application
2. Enter your desired OS name (e.g., "Furrian")
3. Enter version code (e.g., "1.0")
4. Select your preferred desktop environment (e.g., "KDE Plasma")
5. Add packages you want to include (e.g., firefox-esr, libreoffice, vlc)
6. Preview the configuration to verify your settings
7. Click "Build ISO" to create your bootable ISO file
8. Save the ISO to your desired location

## Using the Generated ISO

Once you have created your ISO file, you can:

### 1. Write to USB Drive

**Windows:**
- Use Rufus (https://rufus.ie)
- Select your USB drive
- Select the ISO file
- Click "Start"

**Linux:**
```bash
sudo dd if=mydebianspin-1.0.iso of=/dev/sdX bs=4M status=progress
sync
```

**macOS:**
```bash
sudo dd if=mydebianspin-1.0.iso of=/dev/diskX bs=4m
```

### 2. Use in Virtual Machine

- **VirtualBox**: Create new VM, attach ISO as optical drive
- **VMware**: Create new VM, use ISO as installation media
- **QEMU**: `qemu-system-x86_64 -cdrom mydebianspin-1.0.iso -boot d -m 2048`

### 3. Boot from ISO

1. Insert USB drive or configure VM
2. Boot from the drive
3. Select "Live" mode to try without installing
4. Select "Install" mode to install to hard drive

## Architecture

- **debspin_gui.py**: Main GUI application with tkinter interface
- **iso_builder.py**: ISO creation engine that builds bootable Debian ISOs
- **test_debspin.py**: Test suite for configuration generation

## License

This project is open source and available for use in creating custom Debian distributions.

## About

Debspin makes it easy to create custom Debian spinoffs with a user-friendly graphical interface. Whether you're creating a specialized distribution for development, education, or personal use, Debspin simplifies the entire process from configuration to bootable ISO creation.
