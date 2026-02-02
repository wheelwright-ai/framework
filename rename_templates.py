#!/usr/bin/env python3
"""Rename template directories in the framework."""

import os
import sys
import shutil
from pathlib import Path

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def rename_templates():
    """Rename WAI and HUB template directories."""
    base_path = Path(__file__).parent / "templates"
    
    renames = [
        ("WAI", "WAI-Spoke"),
        ("HUB", "WAI-Hub"),
    ]
    
    results = []
    
    for old_name, new_name in renames:
        old_path = base_path / old_name
        new_path = base_path / new_name
        
        try:
            if not old_path.exists():
                results.append(f"❌ SKIP: {old_path} does not exist")
                continue
            
            if new_path.exists():
                results.append(f"❌ SKIP: {new_path} already exists")
                continue
            
            shutil.move(str(old_path), str(new_path))
            results.append(f"✅ Renamed: {old_name} → {new_name}")
        except Exception as e:
            results.append(f"❌ ERROR: {old_name} → {new_name}: {e}")
    
    # Verify both exist
    results.append("\n--- VERIFICATION ---")
    for old_name, new_name in renames:
        new_path = base_path / new_name
        if new_path.exists():
            results.append(f"✅ VERIFIED: {new_name} exists")
        else:
            results.append(f"❌ FAILED: {new_name} not found")
    
    return results

if __name__ == "__main__":
    print("=" * 50)
    print("Template Directory Rename Script")
    print("=" * 50)
    
    results = rename_templates()
    for result in results:
        print(result)
    
    print("=" * 50)
    print("COMPLETE")
    print("=" * 50)
