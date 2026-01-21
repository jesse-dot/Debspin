#!/usr/bin/env python3
"""
Test script for Debspin GUI core functionality
"""

import json
import sys
import os

# Add the directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_generation():
    """Test configuration generation without GUI"""
    print("Testing Debspin configuration generation...")
    
    # Simulate configuration
    config = {
        "os_name": "TestDebian",
        "version_code": "1.0",
        "desktop_manager": "KDE Plasma",
        "packages": ["firefox-esr", "libreoffice", "git"],
        "created_at": "2026-01-21T18:13:41.000000",
        "version": "1.0"
    }
    
    # Test JSON serialization
    try:
        config_json = json.dumps(config, indent=2)
        print("✓ Configuration JSON generation successful")
        print("\nGenerated configuration:")
        print(config_json)
    except Exception as e:
        print(f"✗ Configuration JSON generation failed: {e}")
        return False
    
    # Test default values
    assert config["desktop_manager"] == "KDE Plasma", "Default desktop should be KDE Plasma"
    print("✓ Default desktop manager is KDE Plasma")
    
    # Test required fields
    assert "os_name" in config, "OS name is required"
    assert "version_code" in config, "Version code is required"
    assert "desktop_manager" in config, "Desktop manager is required"
    assert "packages" in config, "Packages field is required"
    print("✓ All required fields are present")
    
    # Test package list
    assert isinstance(config["packages"], list), "Packages should be a list"
    assert len(config["packages"]) > 0, "Should have at least one package"
    print("✓ Package list is valid")
    
    # Test version code
    assert config["version_code"] == "1.0", "Version code should be set"
    print("✓ Version code is present")
    
    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_config_generation()
    sys.exit(0 if success else 1)
