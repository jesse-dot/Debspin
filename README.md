# Debspin - Debian Spinoff Creator

Debspin is an easy-to-use GUI application for creating custom Debian-based Linux distributions (spinoffs).

## Features

- **Custom OS Name**: Specify the name of your custom Debian distribution
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
- **Configuration Export**: Save your spinoff configuration as a JSON file for later use

## Requirements

- Python 3.x
- tkinter (usually included with Python)

### Installing tkinter

If tkinter is not available on your system, install it using your package manager:

- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **Arch Linux**: `sudo pacman -S tk`

## Usage

### Method 1: Using the launcher script

```bash
./launch_debspin.sh
```

### Method 2: Direct Python execution

```bash
python3 debspin_gui.py
```

## How to Use

1. **Enter OS Name**: Type the name of your custom Debian distribution (e.g., "MyDebianSpin")
2. **Select Desktop Manager**: Choose from the dropdown menu (defaults to KDE Plasma)
3. **Add Packages**: Enter package names, one per line, in the text area
4. **Preview Configuration**: Click "Preview Configuration" to see your settings in JSON format
5. **Save Configuration**: Click "Save Configuration" to export your spinoff settings to a JSON file

## Configuration File Format

The application generates a JSON configuration file with the following structure:

```json
{
  "os_name": "MyDebianSpin",
  "desktop_manager": "KDE Plasma",
  "packages": [
    "firefox-esr",
    "libreoffice",
    "vlc",
    "git",
    "vim",
    "htop"
  ],
  "created_at": "2026-01-21T18:13:41.000000",
  "version": "1.0"
}
```

## Example Workflow

1. Launch the application
2. Enter your desired OS name (e.g., "Furrian")
3. Select your preferred desktop environment (e.g., "KDE Plasma")
4. Add packages you want to include (e.g., firefox-esr, libreoffice, vlc)
5. Preview the configuration to verify your settings
6. Save the configuration file for use with Debian build tools

## License

This project is open source and available for use in creating custom Debian distributions.

## About

Debspin makes it easy to define custom Debian spinoffs with a user-friendly graphical interface. Whether you're creating a specialized distribution for development, education, or personal use, Debspin simplifies the configuration process.
