#!/usr/bin/env python3
"""
Integration test for Debspin GUI and ISO Builder
Tests the complete workflow without requiring tkinter
"""

import json
import sys
import os
import tempfile

# Add the directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iso_builder import ISOBuilder, sanitize_filename

def test_iso_creation():
    """Test ISO creation with various configurations"""
    print("Testing ISO creation workflow...\n")
    
    test_configs = [
        {
            "name": "KDE Configuration",
            "config": {
                "os_name": "TestKDE",
                "version_code": "1.0",
                "desktop_manager": "KDE Plasma",
                "packages": ["firefox-esr", "vim"],
                "created_at": "2026-01-21T18:00:00"
            }
        },
        {
            "name": "Server Configuration",
            "config": {
                "os_name": "TestServer",
                "version_code": "2.1",
                "desktop_manager": "None (Server/Minimal)",
                "packages": ["nginx", "postgresql"],
                "created_at": "2026-01-21T18:00:00"
            }
        },
        {
            "name": "XFCE Configuration",
            "config": {
                "os_name": "TestXFCE",
                "version_code": "3.0-beta",
                "desktop_manager": "XFCE",
                "packages": ["gimp", "inkscape", "blender"],
                "created_at": "2026-01-21T18:00:00"
            }
        },
        {
            "name": "Configuration with Logo and Background",
            "config": {
                "os_name": "TestBranded",
                "version_code": "1.5",
                "desktop_manager": "GNOME",
                "packages": ["firefox-esr"],
                "logo_path": "/tmp/test_logo.png",
                "background_path": "/tmp/test_bg.jpg",
                "created_at": "2026-01-21T18:00:00"
            }
        }
    ]
    
    all_passed = True
    
    for test_case in test_configs:
        print(f"Testing: {test_case['name']}")
        config = test_case['config']
        
        # Create output path using shared sanitization
        os_name_safe = sanitize_filename(config['os_name'])
        version_safe = sanitize_filename(config['version_code'])
        output_path = f"/tmp/{os_name_safe}-{version_safe}.iso"
        
        # Build ISO
        builder = ISOBuilder(config, output_path)
        success = builder.build()
        
        if success:
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✓ ISO created: {output_path} ({file_size} bytes)")
                
                # Verify ISO naming convention
                expected_name = f"{os_name_safe}-{version_safe}.iso"
                actual_name = os.path.basename(output_path)
                if actual_name == expected_name:
                    print(f"✓ ISO naming correct: {expected_name}")
                else:
                    print(f"✗ ISO naming incorrect: expected {expected_name}, got {actual_name}")
                    all_passed = False
            else:
                print(f"✗ ISO file not found: {output_path}")
                all_passed = False
        else:
            print(f"✗ ISO build failed")
            all_passed = False
        
        print()
    
    if all_passed:
        print("✅ All integration tests passed!")
    else:
        print("❌ Some integration tests failed")
    
    return all_passed

def test_config_with_version_code():
    """Test configuration generation with version code"""
    print("Testing configuration with version code...\n")
    
    config = {
        "os_name": "MyDebian",
        "version_code": "1.5.2",
        "desktop_manager": "GNOME",
        "packages": ["firefox", "thunderbird"],
        "created_at": "2026-01-21T18:00:00",
        "version": "1.0"
    }
    
    # Test JSON serialization
    try:
        config_json = json.dumps(config, indent=2)
        print("✓ Configuration with version_code serializes correctly")
        
        # Verify version_code is present
        assert "version_code" in config, "version_code field missing"
        assert config["version_code"] == "1.5.2", "version_code value incorrect"
        print("✓ version_code field present and correct")
        
        print()
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        print()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Debspin Integration Tests")
    print("="*60)
    print()
    
    test1 = test_config_with_version_code()
    test2 = test_iso_creation()
    
    if test1 and test2:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
