#!/usr/bin/env python3
"""
Test script to verify progress callback functionality
"""

import sys
import os
import tempfile

# Add the directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iso_builder import ISOBuilder

def test_progress_callback():
    """Test that progress callback is called with expected values"""
    print("Testing progress callback functionality...\n")
    
    # Track progress updates
    progress_updates = []
    
    def progress_callback(percentage, message):
        progress_updates.append((percentage, message))
        print(f"Progress: {percentage}% - {message}")
    
    # Create test configuration
    config = {
        "os_name": "TestProgress",
        "version_code": "1.0",
        "desktop_manager": "XFCE",
        "packages": ["vim", "git"],
        "created_at": "2026-01-21T18:00:00"
    }
    
    # Create output path using tempfile for cross-platform compatibility
    output_path = os.path.join(tempfile.gettempdir(), "test-progress.iso")
    
    # Build ISO with progress callback
    builder = ISOBuilder(config, output_path, progress_callback)
    success = builder.build()
    
    print("\n" + "="*60)
    print("Progress Updates Summary:")
    print("="*60)
    
    if len(progress_updates) == 0:
        print("❌ FAILED: No progress updates received!")
        return False
    
    print(f"Total progress updates: {len(progress_updates)}")
    print("\nProgress updates received:")
    for i, (percentage, message) in enumerate(progress_updates, 1):
        print(f"  {i}. {percentage}% - {message}")
    
    # Verify we got progress updates
    assert len(progress_updates) > 0, "Should receive progress updates"
    
    # Verify progress starts at 0
    assert progress_updates[0][0] == 0, "First progress should be 0%"
    
    # Verify progress ends at 100
    assert progress_updates[-1][0] == 100, "Last progress should be 100%"
    
    # Verify progress is increasing (generally)
    percentages = [p[0] for p in progress_updates]
    print(f"\nPercentage progression: {percentages}")
    
    # Verify the build was successful
    assert success, "Build should succeed"
    
    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)
    
    print("\n✅ All progress callback tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_progress_callback()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
