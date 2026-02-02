#!/usr/bin/env python3
"""Rename template directories to match capitalization pattern."""
import shutil
from pathlib import Path

framework = Path.cwd()
templates = framework / 'templates'

print("Renaming template directories...")

# Rename WAI -> WAI-Spoke
wai_old = templates / 'WAI'
wai_spoke = templates / 'WAI-Spoke'
if wai_old.exists() and not wai_spoke.exists():
    shutil.move(str(wai_old), str(wai_spoke))
    print(f"✅ Renamed: WAI → WAI-Spoke")
elif wai_spoke.exists():
    print(f"✓ WAI-Spoke already exists")

# Rename HUB -> WAI-Hub
hub_old = templates / 'HUB'
wai_hub = templates / 'WAI-Hub'
if hub_old.exists() and not wai_hub.exists():
    shutil.move(str(hub_old), str(wai_hub))
    print(f"✅ Renamed: HUB → WAI-Hub")
elif wai_hub.exists():
    print(f"✓ WAI-Hub already exists")

# Verify
print("\nTemplate directories:")
for d in sorted(templates.iterdir()):
    if d.is_dir():
        if d.name.startswith('WAI'):
            print(f"  ✓ {d.name}/")
