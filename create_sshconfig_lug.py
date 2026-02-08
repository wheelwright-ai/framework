#!/usr/bin/env python3
"""Create SSH config lug for framework."""

from wai.config import get_config

# Initialize SSH config for framework
config = get_config()

# Create default lug with framework user
lug_path = config.create_default_lug(
    git_user="Wheelwright Framework",
    git_email="framework@wheelwright.ai"
)

print(f"✓ Created SSH config lug: {lug_path}")

# Verify it loads
config_data = config.load_config(force_reload=True)
print(f"✓ Git user: {config_data['git']['user']}")
print(f"✓ Git email: {config_data['git']['email']}")
print(f"✓ SSH key path: {config_data['ssh']['key_path']}")
