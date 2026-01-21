#!/usr/bin/env python3
"""
Debspin - Debian Spinoff Creator
A GUI application for creating custom Debian-based Linux distributions
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import subprocess
import threading
from datetime import datetime


class DebspinGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Debspin - Debian Spinoff Creator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create main container
        main_container = ttk.Frame(root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_container, text="Debian Spinoff Creator", 
                                font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # OS Name section
        os_frame = ttk.LabelFrame(main_container, text="Operating System Details", 
                                  padding="10")
        os_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        os_frame.columnconfigure(1, weight=1)
        
        ttk.Label(os_frame, text="OS Name:").grid(row=0, column=0, sticky=tk.W, 
                                                  padx=(0, 10))
        self.os_name_var = tk.StringVar(value="MyDebianSpin")
        self.os_name_entry = ttk.Entry(os_frame, textvariable=self.os_name_var, 
                                       width=40)
        self.os_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(os_frame, text="Version Code:").grid(row=1, column=0, sticky=tk.W, 
                                                       padx=(0, 10), pady=(5, 0))
        self.version_var = tk.StringVar(value="1.0")
        self.version_entry = ttk.Entry(os_frame, textvariable=self.version_var, 
                                       width=40)
        self.version_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Desktop Manager section
        de_frame = ttk.LabelFrame(main_container, text="Desktop Environment", 
                                  padding="10")
        de_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        de_frame.columnconfigure(1, weight=1)
        
        ttk.Label(de_frame, text="Desktop Manager:").grid(row=0, column=0, 
                                                          sticky=tk.W, padx=(0, 10))
        
        # Desktop manager options
        self.desktop_managers = [
            "KDE Plasma",
            "GNOME",
            "XFCE",
            "LXDE",
            "Cinnamon",
            "MATE",
            "Budgie",
            "i3",
            "None (Server/Minimal)"
        ]
        
        self.desktop_var = tk.StringVar(value="KDE Plasma")
        self.desktop_combo = ttk.Combobox(de_frame, textvariable=self.desktop_var,
                                          values=self.desktop_managers, 
                                          state="readonly", width=37)
        self.desktop_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Packages section
        packages_frame = ttk.LabelFrame(main_container, text="Additional Packages", 
                                       padding="10")
        packages_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        packages_frame.columnconfigure(0, weight=1)
        packages_frame.rowconfigure(1, weight=1)
        
        ttk.Label(packages_frame, 
                 text="Enter package names (one per line):").grid(row=0, column=0, 
                                                                   sticky=tk.W, 
                                                                   pady=(0, 5))
        
        # Package list text area
        self.packages_text = scrolledtext.ScrolledText(packages_frame, 
                                                       width=60, height=10,
                                                       wrap=tk.WORD)
        self.packages_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add some default packages as examples
        default_packages = """firefox-esr
libreoffice
vlc
git
vim
htop"""
        self.packages_text.insert("1.0", default_packages)
        
        # Configuration output section
        config_frame = ttk.LabelFrame(main_container, text="Configuration Preview", 
                                      padding="10")
        config_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                         pady=(0, 10))
        config_frame.columnconfigure(0, weight=1)
        config_frame.rowconfigure(0, weight=1)
        
        self.config_text = scrolledtext.ScrolledText(config_frame, 
                                                     width=60, height=8,
                                                     wrap=tk.WORD, 
                                                     state=tk.DISABLED)
        self.config_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons section
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        self.preview_btn = ttk.Button(button_frame, text="Preview Configuration", 
                                      command=self.preview_config)
        self.preview_btn.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        self.build_btn = ttk.Button(button_frame, text="Build ISO", 
                                   command=self.build_iso)
        self.build_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.about_btn = ttk.Button(button_frame, text="About", 
                                    command=self.show_about)
        self.about_btn.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
        
        # Auto-preview on startup
        self.preview_config()
    
    def get_packages_list(self):
        """Get the list of packages from the text area"""
        packages_content = self.packages_text.get("1.0", tk.END)
        packages = [pkg.strip() for pkg in packages_content.split('\n') 
                   if pkg.strip()]
        return packages
    
    def generate_config(self):
        """Generate the spinoff configuration"""
        config = {
            "os_name": self.os_name_var.get(),
            "version_code": self.version_var.get(),
            "desktop_manager": self.desktop_var.get(),
            "packages": self.get_packages_list(),
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        return config
    
    def preview_config(self):
        """Preview the configuration in JSON format"""
        config = self.generate_config()
        config_json = json.dumps(config, indent=2)
        
        self.config_text.config(state=tk.NORMAL)
        self.config_text.delete("1.0", tk.END)
        self.config_text.insert("1.0", config_json)
        self.config_text.config(state=tk.DISABLED)
    
    def get_desktop_packages(self, desktop_manager):
        """Map desktop manager to required packages"""
        desktop_packages = {
            "KDE Plasma": ["kde-plasma-desktop", "sddm"],
            "GNOME": ["gnome-core", "gdm3"],
            "XFCE": ["xfce4", "xfce4-goodies", "lightdm"],
            "LXDE": ["lxde", "lightdm"],
            "Cinnamon": ["cinnamon-desktop-environment", "lightdm"],
            "MATE": ["mate-desktop-environment", "lightdm"],
            "Budgie": ["budgie-desktop", "lightdm"],
            "i3": ["i3", "lightdm"],
            "None (Server/Minimal)": []
        }
        return desktop_packages.get(desktop_manager, [])
    
    def build_iso(self):
        """Build the Debian ISO"""
        config = self.generate_config()
        
        # Validate inputs
        if not config["os_name"]:
            messagebox.showerror("Error", "Please enter an OS name")
            return
        
        if not config["version_code"]:
            messagebox.showerror("Error", "Please enter a version code")
            return
        
        # Ask for save location
        os_name_safe = config['os_name'].replace(' ', '_').lower()
        version_safe = config['version_code'].replace(' ', '_')
        default_filename = f"{os_name_safe}-{version_safe}.iso"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".iso",
            initialfile=default_filename,
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        # Disable the build button during build
        self.build_btn.config(state=tk.DISABLED, text="Building...")
        self.root.update()
        
        # Build ISO in a separate thread to avoid freezing the GUI
        build_thread = threading.Thread(
            target=self._build_iso_thread,
            args=(config, filepath)
        )
        build_thread.daemon = True
        build_thread.start()
    
    def _build_iso_thread(self, config, output_path):
        """Build the ISO in a separate thread"""
        try:
            # Create the ISO builder and build
            from iso_builder import ISOBuilder
            builder = ISOBuilder(config, output_path)
            success = builder.build()
            
            if success:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"ISO created successfully!\n\nFile: {output_path}\n\n"
                    f"You can now use this ISO to:\n"
                    f"• Create a bootable USB drive\n"
                    f"• Boot in a virtual machine\n"
                    f"• Install {config['os_name']} on a computer"
                ))
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Failed to build ISO. Check console for details."
                ))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Failed to build ISO:\n{str(e)}"
            ))
        finally:
            # Re-enable the build button
            self.root.after(0, lambda: self.build_btn.config(
                state=tk.NORMAL, 
                text="Build ISO"
            ))
    
    def save_config(self):
        """Save the configuration to a file (legacy method)"""
        config = self.generate_config()
        
        # Validate inputs
        if not config["os_name"]:
            messagebox.showerror("Error", "Please enter an OS name")
            return
        
        if not config["packages"]:
            messagebox.showwarning("Warning", 
                                  "No packages specified. Continue anyway?")
        
        # Ask for save location
        default_filename = f"{config['os_name'].replace(' ', '_').lower()}_config.json"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Success", 
                                   f"Configuration saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration:\n{e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Debspin - Debian Spinoff Creator
Version 1.0

A GUI application for creating custom Debian-based 
Linux distributions.

Features:
• Specify custom OS name
• Choose desktop environment
• Add custom packages
• Generate configuration files

© 2026 Debspin Project"""
        
        messagebox.showinfo("About Debspin", about_text)


def main():
    root = tk.Tk()
    app = DebspinGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
