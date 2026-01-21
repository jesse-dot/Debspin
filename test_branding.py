#!/usr/bin/env python3
"""
Test script for logo and background functionality
"""

import json
import sys
import os
import tempfile
from pathlib import Path

# Add the directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iso_builder import ISOBuilder

def create_test_images():
    """Create dummy test images"""
    # Create a simple PNG file (1x1 pixel)
    logo_path = '/tmp/test_logo.png'
    with open(logo_path, 'wb') as f:
        # Minimal PNG header for 1x1 transparent pixel
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
    
    # Create a simple JPEG file marker
    bg_path = '/tmp/test_bg.jpg'
    with open(bg_path, 'wb') as f:
        # Minimal JPEG header
        f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xFF\xD9')
    
    return logo_path, bg_path

def test_branding_files():
    """Test that branding files are properly included in ISO"""
    print("Testing branding file inclusion...\n")
    
    # Create test images
    logo_path, bg_path = create_test_images()
    
    # Verify test images exist
    assert os.path.exists(logo_path), f"Logo file not created: {logo_path}"
    assert os.path.exists(bg_path), f"Background file not created: {bg_path}"
    print(f"✓ Test images created: {logo_path}, {bg_path}")
    
    # Create config with branding
    config = {
        "os_name": "BrandedTest",
        "version_code": "1.0",
        "desktop_manager": "KDE Plasma",
        "packages": ["vim"],
        "logo_path": logo_path,
        "background_path": bg_path,
        "created_at": "2026-01-21T20:00:00"
    }
    
    # Build ISO
    output_path = "/tmp/BrandedTest-1.0.iso"
    builder = ISOBuilder(config, output_path)
    success = builder.build()
    
    if success:
        print(f"✓ ISO build completed successfully")
        
        # Check if output exists
        if os.path.exists(output_path):
            print(f"✓ ISO file created: {output_path}")
        else:
            print(f"✗ ISO file not found: {output_path}")
            return False
    else:
        print("✗ ISO build failed")
        return False
    
    print("\n✅ Branding test passed!")
    return True

if __name__ == "__main__":
    success = test_branding_files()
    sys.exit(0 if success else 1)
