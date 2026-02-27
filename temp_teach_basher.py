import sys
from pathlib import Path
from wai.commands.teach import distribute_teach_command

spoke_path = Path("/home/mario/projects/basher")
hub_path = Path("/mnt/c/code/wheelwright/hub")
framework_path = Path("/mnt/c/code/wheelwright/framework")

success = distribute_teach_command(spoke_path, hub_path, framework_path)
if success:
    print("Successfully taught /home/mario/projects/basher")
else:
    print("Failed to teach /home/mario/projects/basher")
    sys.exit(1)
