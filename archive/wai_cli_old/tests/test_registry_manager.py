"""Tests for registry manager."""

from wai.cli.lib.registry_manager import RegistryManager


def test_registry_mark_missing(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(
        """
{
  "version": "2.0",
  "projects": [
    {"name": "exists", "path": "/tmp"},
    {"name": "missing", "path": "/tmp/does-not-exist"}
  ]
}
"""
    )

    manager = RegistryManager(registry)
    changed = manager.mark_missing()
    assert changed == 1
    data = manager.load()
    statuses = {p["name"]: p.get("status") for p in data["projects"]}
    assert statuses["missing"] == "missing"
