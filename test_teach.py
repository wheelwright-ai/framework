#!/usr/bin/env python3
"""Quick test of teach command for one spoke."""
import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent))

from wai.commands.teach import teach_command
from wai.hub import HubManager

framework_path = Path(__file__).parent
hub_manager = HubManager()
hub_path = hub_manager.auto_discover_hub(Path.cwd(), verbose=False)

# Test with first spoke
spoke_path = Path("/home/mario/projects/wheelwright-ai/framework")

print(f"Testing teach_command:")
print(f"  spoke_path: {spoke_path}")
print(f"  hub_path: {hub_path}")
print(f"  framework_path: {framework_path}\n")

try:
    result = teach_command(spoke_path, hub_path, framework_path)
    print(f"\nResult: {result}")
except Exception as e:
    import traceback
    print(f"\n\nERROR: {type(e).__name__}")
    print(f"Message: {e}")
    print(f"\nFull traceback:")
    traceback.print_exc()
