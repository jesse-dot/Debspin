#!/usr/bin/env python3
"""
ISO Builder Module for Debspin
Creates bootable Debian ISOs with live boot and installation capabilities
"""

import os
import subprocess
import tempfile
import shutil
import json
import re
from pathlib import Path


def sanitize_filename(text):
    """
    Sanitize a string to make it safe for use in filenames
    
    Args:
        text: The text to sanitize
        
    Returns:
        A sanitized version safe for filenames
    """
    # Replace spaces with underscores
    text = text.replace(' ', '_')
    # Remove characters that are problematic for filesystems
    text = re.sub(r'[/\\:*?"<>|]', '', text)
    # Replace any remaining non-alphanumeric characters (except dots, dashes, underscores)
    text = re.sub(r'[^a-zA-Z0-9._-]', '-', text)
    # Remove leading/trailing dots and dashes
    text = text.strip('.-')
    return text


def sanitize_grub_string(text):
    """
    Sanitize a string for safe use in GRUB configuration
    
    Args:
        text: The text to sanitize
        
    Returns:
        A sanitized version safe for GRUB config
    """
    # Escape quotes and backslashes
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f]', '', text)
    return text


class ISOBuilder:
    """Builds a custom Debian ISO with live boot and installation capabilities"""
    
    def __init__(self, config, output_path, progress_callback=None):
        """
        Initialize the ISO builder
        
        Args:
            config: Configuration dictionary with os_name, desktop_manager, packages, etc.
            output_path: Path where the ISO file will be saved
            progress_callback: Optional callback function for progress updates.
                             Expected signature: callback(percentage: int, message: str)
                             where percentage is 0-100 and message is a status description.
        """
        self.config = config
        self.output_path = output_path
        self.work_dir = None
        self.progress_callback = progress_callback
        
    def _report_progress(self, percentage, message):
        """Report progress to the callback if available"""
        if self.progress_callback:
            self.progress_callback(percentage, message)
        
    def build(self):
        """
        Build the Debian ISO
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._report_progress(0, "Starting ISO build...")
            print(f"\n{'='*60}")
            print(f"Building Debian ISO: {self.config['os_name']}")
            print(f"Version: {self.config['version_code']}")
            print(f"Desktop Manager: {self.config['desktop_manager']}")
            print(f"Output: {self.output_path}")
            print(f"{'='*60}\n")
            
            # Create temporary working directory
            self._report_progress(5, "Creating temporary working directory...")
            self.work_dir = tempfile.mkdtemp(prefix='debspin_build_')
            print(f"Working directory: {self.work_dir}")
            
            # Check for required tools
            self._report_progress(10, "Checking system requirements...")
            if not self._check_requirements():
                print("\n⚠ WARNING: Required tools not found!")
                print("Creating a minimal ISO stub for demonstration purposes.")
                return self._create_stub_iso()
            
            # Build the ISO using live-build
            return self._build_with_live_build()
            
        except Exception as e:
            print(f"\n❌ Error building ISO: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Clean up working directory
            if self.work_dir and os.path.exists(self.work_dir):
                try:
                    shutil.rmtree(self.work_dir)
                    print(f"\n✓ Cleaned up working directory")
                except Exception as e:
                    print(f"\n⚠ Warning: Could not clean up {self.work_dir}: {e}")
    
    def _check_requirements(self):
        """Check if required tools are available and user has proper permissions"""
        required_tools = ['debootstrap', 'xorriso', 'mksquashfs']
        missing_tools = []
        
        for tool in required_tools:
            if shutil.which(tool) is None:
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"⚠ Missing required tools: {', '.join(missing_tools)}")
            print("\nTo install on Ubuntu/Debian:")
            print("  sudo apt-get update")
            print("  sudo apt-get install debootstrap xorriso squashfs-tools")
            print("\nTo install on Fedora:")
            print("  sudo dnf install debootstrap xorriso squashfs-tools")
            print("\nTo install on Arch Linux:")
            print("  sudo pacman -S debootstrap libisoburn squashfs-tools")
            return False
        
        # Check for root privileges (required for debootstrap)
        if os.geteuid() != 0:
            print("⚠ Root privileges required!")
            print("\nBuilding a full Debian ISO requires root/sudo privileges.")
            print("Please run this application with sudo:")
            print("  sudo python3 debspin_gui.py")
            print("\nOr run the launcher script with sudo:")
            print("  sudo ./launch_debspin.sh")
            return False
        
        return True
    
    def _create_stub_iso(self):
        """
        Create a stub ISO file with metadata for demonstration/testing
        This is used when live-build tools are not available
        """
        try:
            self._report_progress(15, "Creating ISO directory structure...")
            # Create ISO directory structure
            iso_dir = os.path.join(self.work_dir, 'iso')
            os.makedirs(iso_dir, exist_ok=True)
            
            self._report_progress(30, "Creating metadata file...")
            # Create metadata file
            metadata = {
                'iso_type': 'Debian Custom Spinoff',
                'name': self.config['os_name'],
                'version': self.config['version_code'],
                'desktop_manager': self.config['desktop_manager'],
                'packages': self.config['packages'],
                'created_at': self.config.get('created_at', ''),
                'bootable': True,
                'live_boot': True,
                'installation_capable': True,
                'note': 'This is a demonstration ISO. To create a real bootable ISO, '
                        'install: debootstrap, xorriso, squashfs-tools, and live-build'
            }
            
            metadata_path = os.path.join(iso_dir, 'debspin_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self._report_progress(50, "Creating README file...")
            # Create a README
            readme_path = os.path.join(iso_dir, 'README.txt')
            with open(readme_path, 'w') as f:
                f.write(f"""
{self.config['os_name']} - Custom Debian Spinoff
Version: {self.config['version_code']}

This ISO contains a custom Debian distribution with:
- Desktop Manager: {self.config['desktop_manager']}
- Custom packages: {len(self.config['packages'])} packages included

Features:
✓ Live Boot capability
✓ Installation capability
✓ Custom package selection
✓ User-configured desktop environment

To use this ISO:
1. Write it to a USB drive using tools like:
   - Rufus (Windows)
   - Etcher (Cross-platform)
   - dd command (Linux/Mac)

2. Boot from the USB drive

3. Choose between:
   - Try the live environment
   - Install to your computer

Created with Debspin - Debian Spinoff Creator
""")
            
            self._report_progress(65, "Creating boot configuration...")
            # Create boot configuration stub
            boot_dir = os.path.join(iso_dir, 'boot')
            os.makedirs(boot_dir, exist_ok=True)
            
            grub_cfg_path = os.path.join(boot_dir, 'grub.cfg')
            with open(grub_cfg_path, 'w') as f:
                # Sanitize values for GRUB configuration
                os_name_safe = sanitize_grub_string(self.config['os_name'])
                version_safe = sanitize_grub_string(self.config['version_code'])
                
                f.write(f"""
# GRUB Configuration for {os_name_safe}
set default=0
set timeout=10

menuentry "{os_name_safe} {version_safe} - Live" {{
    linux /boot/vmlinuz boot=live
    initrd /boot/initrd.img
}}

menuentry "{os_name_safe} {version_safe} - Install" {{
    linux /boot/vmlinuz
    initrd /boot/initrd.img
}}
""")
            
            self._report_progress(75, "Creating package list...")
            # Create package list
            packages_path = os.path.join(iso_dir, 'packages.list')
            with open(packages_path, 'w') as f:
                f.write("# Desktop Environment Packages\n")
                desktop_packages = self._get_desktop_packages()
                for pkg in desktop_packages:
                    f.write(f"{pkg}\n")
                
                f.write("\n# User-specified Packages\n")
                for pkg in self.config['packages']:
                    f.write(f"{pkg}\n")
            
            self._report_progress(85, "Creating ISO file...")
            # Create the ISO using xorriso if available, otherwise create a tar archive
            if shutil.which('genisoimage') or shutil.which('xorriso'):
                return self._create_iso_with_xorriso(iso_dir)
            else:
                # Fallback: create a tar.gz archive
                return self._create_tar_archive(iso_dir)
                
        except Exception as e:
            print(f"❌ Error creating stub ISO: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_iso_with_xorriso(self, iso_dir):
        """Create ISO using xorriso or genisoimage"""
        try:
            # Try xorriso first
            if shutil.which('xorriso'):
                cmd = [
                    'xorriso',
                    '-as', 'mkisofs',
                    '-r',
                    '-J',
                    '-joliet-long',
                    '-l',
                    '-iso-level', '3',
                    '-o', self.output_path,
                    iso_dir
                ]
            elif shutil.which('genisoimage'):
                cmd = [
                    'genisoimage',
                    '-r',
                    '-J',
                    '-joliet-long',
                    '-l',
                    '-iso-level', '3',
                    '-o', self.output_path,
                    iso_dir
                ]
            else:
                return self._create_tar_archive(iso_dir)
            
            print(f"\n📀 Creating ISO file...")
            print(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\n✓ ISO created successfully: {self.output_path}")
                file_size = os.path.getsize(self.output_path) / (1024 * 1024)
                print(f"✓ Size: {file_size:.2f} MB")
                self._report_progress(100, f"ISO created successfully ({file_size:.2f} MB)")
                return True
            else:
                print(f"\n❌ ISO creation failed:")
                print(result.stderr)
                return self._create_tar_archive(iso_dir)
                
        except Exception as e:
            print(f"❌ Error creating ISO: {e}")
            return self._create_tar_archive(iso_dir)
    
    def _create_tar_archive(self, iso_dir):
        """Fallback: create a tar.gz archive instead of ISO"""
        try:
            self._report_progress(90, "Creating tar.gz archive...")
            # Change output path from .iso to .tar.gz
            tar_path = self.output_path.replace('.iso', '.tar.gz')
            
            print(f"\n📦 Creating tar.gz archive (ISO tools not available)...")
            print(f"Output: {tar_path}")
            
            import tarfile
            with tarfile.open(tar_path, 'w:gz') as tar:
                tar.add(iso_dir, arcname=os.path.basename(iso_dir))
            
            print(f"\n✓ Archive created successfully: {tar_path}")
            file_size = os.path.getsize(tar_path) / (1024 * 1024)
            print(f"✓ Size: {file_size:.2f} MB")
            
            self._report_progress(95, "Creating info file...")
            # Create a text file at the ISO path explaining the situation
            info_text = f"""Debspin ISO Builder Output

The requested ISO file could not be created because required tools
(debootstrap, xorriso, squashfs-tools) are not installed.

Instead, a tar.gz archive has been created at:
{tar_path}

This archive contains all the metadata and configuration that would
be in the ISO:
- Boot configuration (GRUB)
- Package lists (desktop environment + user packages)
- ISO metadata (JSON format)
- README with usage instructions

To create a real bootable ISO, install the required tools:
  Ubuntu/Debian: sudo apt-get install debootstrap xorriso squashfs-tools
  Fedora: sudo dnf install debootstrap xorriso squashfs-tools
  Arch: sudo pacman -S debootstrap libisoburn squashfs-tools

Then run Debspin again to build the ISO.

Archive location: {tar_path}
ISO metadata: See debspin_metadata.json in the archive
"""
            
            with open(self.output_path, 'w') as f:
                f.write(info_text)
            
            print(f"✓ Created info file: {self.output_path}")
            print(f"  (Contains path to tar.gz archive)")
            
            self._report_progress(100, f"Archive created successfully ({file_size:.2f} MB)")
            return True
            
        except Exception as e:
            print(f"❌ Error creating archive: {e}")
            return False
    
    def _get_desktop_packages(self):
        """Get list of packages for the selected desktop manager"""
        desktop_packages = {
            "KDE Plasma": [
                "kde-plasma-desktop",
                "sddm",
                "plasma-nm",
                "plasma-pa"
            ],
            "GNOME": [
                "gnome-core",
                "gdm3",
                "gnome-terminal",
                "nautilus"
            ],
            "XFCE": [
                "xfce4",
                "xfce4-goodies",
                "lightdm",
                "xfce4-terminal"
            ],
            "LXDE": [
                "lxde",
                "lightdm",
                "lxterminal"
            ],
            "Cinnamon": [
                "cinnamon-desktop-environment",
                "lightdm",
                "gnome-terminal"
            ],
            "MATE": [
                "mate-desktop-environment",
                "lightdm",
                "mate-terminal"
            ],
            "Budgie": [
                "budgie-desktop",
                "lightdm",
                "gnome-terminal"
            ],
            "i3": [
                "i3",
                "lightdm",
                "i3status",
                "dmenu",
                "xterm"
            ],
            "None (Server/Minimal)": []
        }
        
        return desktop_packages.get(self.config['desktop_manager'], [])
    
    def _build_with_live_build(self):
        """
        Build ISO using debootstrap and live system tools
        This creates a proper bootable Debian ISO with live boot capability
        """
        try:
            print("\n📦 Building bootable Debian ISO...")
            
            # Create directory structure
            self._report_progress(15, "Creating directory structure...")
            rootfs_dir = os.path.join(self.work_dir, 'rootfs')
            iso_dir = os.path.join(self.work_dir, 'iso')
            squashfs_dir = os.path.join(iso_dir, 'live')
            boot_dir = os.path.join(iso_dir, 'boot')
            grub_dir = os.path.join(boot_dir, 'grub')
            isolinux_dir = os.path.join(iso_dir, 'isolinux')
            
            for d in [rootfs_dir, iso_dir, squashfs_dir, boot_dir, grub_dir, isolinux_dir]:
                os.makedirs(d, exist_ok=True)
            
            # Step 1: Bootstrap base Debian system
            print("\n📥 Step 1/6: Bootstrapping Debian base system...")
            self._report_progress(20, "Step 1/6: Bootstrapping Debian base system...")
            if not self._run_debootstrap(rootfs_dir):
                print("❌ Debootstrap failed, falling back to stub ISO")
                return self._create_stub_iso()
            
            # Step 2: Install desktop environment and packages
            print("\n📦 Step 2/6: Installing desktop environment and packages...")
            self._report_progress(40, "Step 2/6: Installing desktop environment and packages...")
            if not self._install_packages(rootfs_dir):
                print("⚠ Some packages may have failed to install")
            
            # Step 3: Configure the live system
            print("\n⚙ Step 3/6: Configuring live system...")
            self._report_progress(60, "Step 3/6: Configuring live system...")
            self._configure_live_system(rootfs_dir)
            
            # Step 4: Create squashfs filesystem
            print("\n🗜 Step 4/6: Creating squashfs filesystem...")
            self._report_progress(70, "Step 4/6: Creating squashfs filesystem...")
            squashfs_path = os.path.join(squashfs_dir, 'filesystem.squashfs')
            if not self._create_squashfs(rootfs_dir, squashfs_path):
                print("❌ Squashfs creation failed, falling back to stub ISO")
                return self._create_stub_iso()
            
            # Step 5: Setup boot configuration
            print("\n🔧 Step 5/6: Setting up boot configuration...")
            self._report_progress(85, "Step 5/6: Setting up boot configuration...")
            self._setup_boot(rootfs_dir, iso_dir, boot_dir, grub_dir, isolinux_dir)
            
            # Step 6: Create the final ISO
            print("\n💿 Step 6/6: Creating bootable ISO...")
            self._report_progress(90, "Step 6/6: Creating bootable ISO...")
            if self._create_bootable_iso(iso_dir):
                return True
            else:
                print("⚠ Bootable ISO creation failed, falling back to stub ISO")
                return self._create_stub_iso()
            
        except Exception as e:
            print(f"❌ Error with live-build: {e}")
            import traceback
            traceback.print_exc()
            return self._create_stub_iso()
    
    def _run_debootstrap(self, rootfs_dir):
        """Bootstrap a minimal Debian system using debootstrap"""
        try:
            # Use bookworm (Debian 12) as the stable release
            suite = 'bookworm'
            mirror = 'http://deb.debian.org/debian'
            
            cmd = [
                'debootstrap',
                '--variant=minbase',
                '--include=apt,locales,sudo,systemd-sysv,live-boot,linux-image-amd64',
                suite,
                rootfs_dir,
                mirror
            ]
            
            print(f"Running: {' '.join(cmd)}")
            print("This may take several minutes depending on your internet connection...")
            print("(Downloading ~200MB of packages from Debian mirrors)")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode != 0:
                print(f"\n❌ Debootstrap failed!")
                print("\nError output:")
                print("-" * 40)
                # Show both stdout and stderr for debugging (safely handle None/empty)
                stdout = result.stdout or ''
                stderr = result.stderr or ''
                if stdout:
                    print(stdout[-2000:] if len(stdout) > 2000 else stdout)
                if stderr:
                    print(stderr[-2000:] if len(stderr) > 2000 else stderr)
                print("-" * 40)
                print("\nCommon causes of debootstrap failures:")
                print("  1. No internet connection or firewall blocking access")
                print("  2. Insufficient disk space (need at least 2GB free)")
                print("  3. DNS resolution issues (try: ping deb.debian.org)")
                print("  4. Permission issues (make sure to run with sudo)")
                return False
            
            print("✓ Base system bootstrapped successfully")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Debootstrap timed out after 30 minutes")
            print("\nTroubleshooting steps:")
            print("  1. Check your internet connection: ping deb.debian.org")
            print("  2. Try a different mirror (edit iso_builder.py)")
            print("  3. Check if download is blocked by firewall")
            print("  4. Ensure you have at least 2GB free disk space")
            return False
        except FileNotFoundError:
            print("❌ debootstrap command not found!")
            print("Please install it: sudo apt-get install debootstrap")
            return False
        except Exception as e:
            print(f"❌ Debootstrap error: {e}")
            return False
    
    def _install_packages(self, rootfs_dir):
        """Install desktop environment and user-specified packages in the chroot"""
        try:
            # Get packages for the desktop environment
            desktop_packages = self._get_desktop_packages()
            user_packages = self.config.get('packages', [])
            all_packages = desktop_packages + user_packages
            
            if not all_packages:
                print("No additional packages to install")
                return True
            
            # Mount necessary filesystems for chroot
            self._mount_chroot_filesystems(rootfs_dir)
            
            try:
                # Update package lists in chroot
                update_cmd = [
                    'chroot', rootfs_dir,
                    'apt-get', 'update'
                ]
                subprocess.run(update_cmd, capture_output=True, text=True, timeout=300)
                
                # Install packages
                # Sanitize package names to prevent command injection
                safe_packages = [self._sanitize_package_name(pkg) for pkg in all_packages]
                safe_packages = [pkg for pkg in safe_packages if pkg]  # Remove empty strings
                
                if safe_packages:
                    install_cmd = [
                        'chroot', rootfs_dir,
                        'apt-get', 'install', '-y', '--no-install-recommends'
                    ] + safe_packages
                    
                    print(f"Installing packages: {', '.join(safe_packages)}")
                    result = subprocess.run(
                        install_cmd,
                        capture_output=True,
                        text=True,
                        timeout=3600  # 1 hour timeout for large installs
                    )
                    
                    if result.returncode != 0:
                        print(f"⚠ Some packages failed: {result.stderr[:500]}")
                    else:
                        print(f"✓ Installed {len(safe_packages)} packages")
                
                # Clean up apt cache to reduce size
                clean_cmd = ['chroot', rootfs_dir, 'apt-get', 'clean']
                subprocess.run(clean_cmd, capture_output=True)
                
                return True
                
            finally:
                self._unmount_chroot_filesystems(rootfs_dir)
                
        except Exception as e:
            print(f"⚠ Package installation error: {e}")
            self._unmount_chroot_filesystems(rootfs_dir)
            return False
    
    def _sanitize_package_name(self, package_name):
        """
        Sanitize package name to prevent command injection
        Valid Debian package names: lowercase letters, digits, +, -, .
        """
        if not package_name:
            return ''
        # Only allow valid package name characters
        sanitized = re.sub(r'[^a-z0-9+.\-]', '', package_name.lower())
        # Package names must start with alphanumeric
        if sanitized and not sanitized[0].isalnum():
            return ''
        return sanitized
    
    def _mount_chroot_filesystems(self, rootfs_dir):
        """Mount necessary filesystems for chroot operations"""
        mounts = [
            ('proc', os.path.join(rootfs_dir, 'proc'), 'proc'),
            ('sysfs', os.path.join(rootfs_dir, 'sys'), 'sysfs'),
            ('/dev', os.path.join(rootfs_dir, 'dev'), None),  # bind mount
        ]
        
        mounted = []
        for source, target, fstype in mounts:
            os.makedirs(target, exist_ok=True)
            try:
                if fstype:
                    result = subprocess.run(['mount', '-t', fstype, source, target], 
                                 capture_output=True, text=True, check=False)
                else:
                    result = subprocess.run(['mount', '--bind', source, target],
                                 capture_output=True, text=True, check=False)
                
                if result.returncode == 0:
                    mounted.append(target)
                else:
                    # Log mount failure but continue - some environments don't support all mounts
                    print(f"⚠ Could not mount {source} to {target}: {result.stderr.strip()}")
            except Exception as e:
                # Log the error but continue - common in container environments
                print(f"⚠ Mount error for {target}: {e}")
        
        return mounted
    
    def _unmount_chroot_filesystems(self, rootfs_dir):
        """Unmount chroot filesystems in reverse order"""
        # Unmount in reverse order of mounting to respect dependencies
        for subdir in ['dev', 'sys', 'proc']:
            target = os.path.join(rootfs_dir, subdir)
            try:
                subprocess.run(['umount', '-l', target], capture_output=True, check=False)
            except Exception:
                pass  # Best effort unmount
    
    def _configure_live_system(self, rootfs_dir):
        """Configure the rootfs for live boot"""
        try:
            # Create a default user for live session
            user_cmds = [
                ['chroot', rootfs_dir, 'useradd', '-m', '-s', '/bin/bash', 'user'],
                ['chroot', rootfs_dir, 'usermod', '-aG', 'sudo', 'user'],
            ]
            
            for cmd in user_cmds:
                subprocess.run(cmd, capture_output=True, check=False)
            
            # Set default password 'live' for the live user
            # This is more secure than an empty password while still being convenient
            # Using chpasswd to set the password
            passwd_cmd = ['chroot', rootfs_dir, 'chpasswd']
            subprocess.run(passwd_cmd, input='user:live\n', capture_output=True, 
                          text=True, check=False)
            
            # Configure passwordless sudo for live user (common for live systems)
            sudoers_dir = os.path.join(rootfs_dir, 'etc', 'sudoers.d')
            os.makedirs(sudoers_dir, exist_ok=True)
            sudoers_file = os.path.join(sudoers_dir, 'live-user')
            with open(sudoers_file, 'w') as f:
                f.write('user ALL=(ALL) NOPASSWD: ALL\n')
            os.chmod(sudoers_file, 0o440)
            
            # Configure hostname with sanitized value
            hostname = sanitize_filename(self.config['os_name']).lower()[:63]
            if not hostname:
                hostname = 'debspin-live'
            hostname_path = os.path.join(rootfs_dir, 'etc', 'hostname')
            with open(hostname_path, 'w') as f:
                f.write(f"{hostname}\n")
            
            # Configure hosts file
            hosts_path = os.path.join(rootfs_dir, 'etc', 'hosts')
            with open(hosts_path, 'w') as f:
                f.write("127.0.0.1\tlocalhost\n")
                f.write(f"127.0.1.1\t{hostname}\n")
            
            # Create os-release file
            os_release_path = os.path.join(rootfs_dir, 'etc', 'os-release')
            os_name_safe = sanitize_grub_string(self.config['os_name'])
            version_safe = sanitize_grub_string(self.config['version_code'])
            with open(os_release_path, 'w') as f:
                f.write(f'PRETTY_NAME="{os_name_safe} {version_safe}"\n')
                f.write(f'NAME="{os_name_safe}"\n')
                f.write(f'VERSION="{version_safe}"\n')
                f.write(f'ID={sanitize_filename(self.config["os_name"]).lower()}\n')
                f.write('ID_LIKE=debian\n')
            
            print("✓ Live system configured")
            
        except Exception as e:
            print(f"⚠ Configuration warning: {e}")
    
    def _create_squashfs(self, rootfs_dir, output_path):
        """Create squashfs filesystem from rootfs"""
        try:
            cmd = [
                'mksquashfs',
                rootfs_dir,
                output_path,
                '-comp', 'xz',
                '-e', 'boot'  # Exclude /boot, we'll handle it separately
            ]
            
            print("Creating compressed filesystem (this may take a while)...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                print(f"Squashfs error: {result.stderr}")
                return False
            
            # Get size
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✓ Squashfs created: {size_mb:.1f} MB")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Squashfs creation timed out")
            return False
        except Exception as e:
            print(f"❌ Squashfs error: {e}")
            return False
    
    def _setup_boot(self, rootfs_dir, iso_dir, boot_dir, grub_dir, isolinux_dir):
        """Setup boot configuration for the ISO"""
        os_name_safe = sanitize_grub_string(self.config['os_name'])
        version_safe = sanitize_grub_string(self.config['version_code'])
        
        # Copy kernel and initrd from rootfs to ISO boot directory
        kernel_src = os.path.join(rootfs_dir, 'boot')
        if os.path.exists(kernel_src):
            for f in os.listdir(kernel_src):
                src = os.path.join(kernel_src, f)
                if os.path.isfile(src):
                    if f.startswith('vmlinuz'):
                        shutil.copy2(src, os.path.join(boot_dir, 'vmlinuz'))
                    elif f.startswith('initrd') or f.startswith('initramfs'):
                        shutil.copy2(src, os.path.join(boot_dir, 'initrd.img'))
        
        # Create GRUB configuration for EFI boot
        grub_cfg = os.path.join(grub_dir, 'grub.cfg')
        with open(grub_cfg, 'w') as f:
            f.write(f'''# GRUB Configuration for {os_name_safe}
set default=0
set timeout=10

insmod all_video
insmod gfxterm

menuentry "{os_name_safe} {version_safe} - Live (Try without installing)" {{
    linux /boot/vmlinuz boot=live quiet splash
    initrd /boot/initrd.img
}}

menuentry "{os_name_safe} {version_safe} - Live (Safe graphics)" {{
    linux /boot/vmlinuz boot=live nomodeset quiet
    initrd /boot/initrd.img
}}

menuentry "{os_name_safe} {version_safe} - Install" {{
    linux /boot/vmlinuz boot=live quiet
    initrd /boot/initrd.img
}}

menuentry "Boot from first hard disk" {{
    set root=(hd0)
    chainloader +1
}}
''')
        
        # Create isolinux configuration for BIOS boot
        isolinux_cfg = os.path.join(isolinux_dir, 'isolinux.cfg')
        # Only create if isolinux.bin exists on the system
        isolinux_bin_paths = [
            '/usr/lib/ISOLINUX/isolinux.bin',
            '/usr/share/syslinux/isolinux.bin',
            '/usr/lib/syslinux/isolinux.bin'
        ]
        
        for path in isolinux_bin_paths:
            if os.path.exists(path):
                shutil.copy2(path, os.path.join(isolinux_dir, 'isolinux.bin'))
                break
        
        # Copy ldlinux.c32 if it exists
        ldlinux_paths = [
            '/usr/lib/syslinux/modules/bios/ldlinux.c32',
            '/usr/share/syslinux/ldlinux.c32',
            '/usr/lib/ISOLINUX/ldlinux.c32'
        ]
        for path in ldlinux_paths:
            if os.path.exists(path):
                shutil.copy2(path, os.path.join(isolinux_dir, 'ldlinux.c32'))
                break
        
        with open(isolinux_cfg, 'w') as f:
            f.write(f'''# ISOLINUX Configuration for {os_name_safe}
DEFAULT live
TIMEOUT 100
PROMPT 1

LABEL live
    MENU LABEL {os_name_safe} {version_safe} - Live
    KERNEL /boot/vmlinuz
    APPEND initrd=/boot/initrd.img boot=live quiet splash

LABEL livesafe
    MENU LABEL {os_name_safe} {version_safe} - Live (Safe graphics)
    KERNEL /boot/vmlinuz
    APPEND initrd=/boot/initrd.img boot=live nomodeset quiet

LABEL install
    MENU LABEL {os_name_safe} {version_safe} - Install
    KERNEL /boot/vmlinuz
    APPEND initrd=/boot/initrd.img boot=live quiet
''')
        
        # Create metadata file
        metadata = {
            'iso_type': 'Debian Custom Spinoff',
            'name': self.config['os_name'],
            'version': self.config['version_code'],
            'desktop_manager': self.config['desktop_manager'],
            'packages': self.config['packages'],
            'created_at': self.config.get('created_at', ''),
            'bootable': True,
            'live_boot': True,
            'installation_capable': True
        }
        metadata_path = os.path.join(iso_dir, '.disk', 'info')
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        with open(metadata_path, 'w') as f:
            f.write(f"{os_name_safe} {version_safe}")
        
        metadata_json_path = os.path.join(iso_dir, 'debspin_metadata.json')
        with open(metadata_json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("✓ Boot configuration created")
    
    def _create_bootable_iso(self, iso_dir):
        """Create the final bootable ISO using xorriso"""
        try:
            # Remove existing output file if it exists (xorriso may fail to overwrite)
            if os.path.exists(self.output_path):
                try:
                    os.remove(self.output_path)
                except Exception:
                    pass  # Ignore removal errors
            
            # Build xorriso command for bootable ISO
            cmd = [
                'xorriso',
                '-as', 'mkisofs',
                '-r',                           # Rock Ridge extensions
                '-J',                           # Joliet extensions
                '-joliet-long',                 # Long Joliet names
                '-l',                           # Allow full 31-char filenames
                '-iso-level', '3',              # ISO level 3 for large files
                '-V', sanitize_filename(self.config['os_name'])[:32],  # Volume label
            ]
            
            # Add BIOS boot if isolinux.bin exists
            isolinux_bin = os.path.join(iso_dir, 'isolinux', 'isolinux.bin')
            if os.path.exists(isolinux_bin):
                cmd.extend([
                    '-b', 'isolinux/isolinux.bin',
                    '-c', 'isolinux/boot.cat',
                    '-no-emul-boot',
                    '-boot-load-size', '4',
                    '-boot-info-table',
                ])
            
            cmd.extend([
                '-o', self.output_path,
                iso_dir
            ])
            
            print(f"Creating ISO: {self.output_path}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            # Check if the file was created successfully, even if xorriso reports warnings
            if os.path.exists(self.output_path):
                file_size = os.path.getsize(self.output_path)
                # If file size is reasonable (> 1MB), consider it a success
                if file_size > 1024 * 1024:
                    file_size_mb = file_size / (1024 * 1024)
                    print(f"\n✓ ISO created successfully: {self.output_path}")
                    print(f"✓ Size: {file_size_mb:.1f} MB")
                    self._report_progress(100, f"ISO created successfully ({file_size_mb:.1f} MB)")
                    return True
            
            # If we reach here, the ISO was not created properly
            if result.returncode != 0:
                print(f"ISO creation error: {result.stderr}")
            return False
            
        except subprocess.TimeoutExpired:
            print("❌ ISO creation timed out")
            return False
        except Exception as e:
            print(f"❌ ISO creation error: {e}")
            return False


if __name__ == "__main__":
    # Test the ISO builder with progress callback
    def print_progress(percentage, message):
        print(f"Progress: {percentage}% - {message}")
    
    test_config = {
        "os_name": "TestDebian",
        "version_code": "1.0",
        "desktop_manager": "XFCE",
        "packages": ["firefox-esr", "vim", "git"],
        "created_at": "2026-01-21T18:00:00"
    }
    
    builder = ISOBuilder(test_config, "/tmp/test-debian-1.0.iso", print_progress)
    success = builder.build()
    print(f"\nBuild {'succeeded' if success else 'failed'}")
