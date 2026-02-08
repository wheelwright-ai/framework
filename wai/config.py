"""
SSH/Git Configuration - Load and manage wheel-specific SSH and git settings.

Stores configuration in lugs (sshconfig-*.lug.json) allowing per-wheel customization.
Skills access configuration via this module instead of hardcoded facts.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone


class SSHGitConfig:
    """Load and access SSH/git configuration from lugs."""

    # Default configuration template
    DEFAULT_CONFIG = {
        "ssh": {
            "key_path": "~/.ssh/id_ed25519",
            "key_type": "ed25519",
            "key_passphrase": None,
            "verify_command": "ssh -T git@github.com",
        },
        "git": {
            "user": "User Name",
            "email": "user@example.com",
            "author_format": "User Name <user@example.com>",
            "default_remote": "origin",
            "default_branch": "main",
        },
        "github": {
            "host": "github.com",
            "api_endpoint": "https://api.github.com",
            "remote_format": "git@github.com:{owner}/{repo}.git",
        },
    }

    def __init__(self, spoke_path: str = None):
        """
        Initialize config loader.
        
        Args:
            spoke_path: Path to WAI-Spoke directory. If None, searches upward.
        """
        self.spoke_path = self._find_spoke_path(spoke_path)
        self.lugs_dir = Path(self.spoke_path) / "lugs"
        self.lugs_dir.mkdir(parents=True, exist_ok=True)
        self._config = None

    def _find_spoke_path(self, explicit_path: Optional[str]) -> str:
        """Find WAI-Spoke directory."""
        if explicit_path and Path(explicit_path).exists():
            return explicit_path
        
        current = Path.cwd()
        while current != current.parent:
            if (current / "WAI-Spoke").exists():
                return str(current / "WAI-Spoke")
            current = current.parent
        
        raise RuntimeError("WAI-Spoke directory not found. Ensure you're in a Wheelwright project.")

    def _find_sshconfig_lug(self) -> Optional[Path]:
        """Find sshconfig-*.lug.json file."""
        if not self.lugs_dir.exists():
            return None
        
        for f in self.lugs_dir.glob("sshconfig-*.lug.json"):
            return f
        
        return None

    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load SSH/git configuration from lug.
        
        If no lug exists, returns default config.
        
        Args:
            force_reload: Force reload from disk
        
        Returns:
            Configuration dict with ssh, git, github keys
        """
        if self._config and not force_reload:
            return self._config.copy()
        
        # Try to find existing lug
        lug_file = self._find_sshconfig_lug()
        
        if lug_file:
            try:
                with open(lug_file, 'r') as f:
                    lug = json.load(f)
                    # Extract ssh, git, github sections
                    self._config = {
                        "ssh": lug.get("ssh", self.DEFAULT_CONFIG["ssh"]),
                        "git": lug.get("git", self.DEFAULT_CONFIG["git"]),
                        "github": lug.get("github", self.DEFAULT_CONFIG["github"]),
                    }
                    return self._config.copy()
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return defaults
        self._config = {k: v.copy() for k, v in self.DEFAULT_CONFIG.items()}
        return self._config.copy()

    def create_default_lug(self, git_user: str, git_email: str) -> Path:
        """
        Create a new sshconfig lug with provided user info.
        
        Args:
            git_user: Git user name (e.g., "Mario Vaccari")
            git_email: Git email (e.g., "mario@example.com")
        
        Returns:
            Path to created lug file
        """
        lug = {
            "id": f"sshconfig-{self._generate_wheel_id()}",
            "type": "sshconfig",
            "wheel_id": self._get_wheel_id(),
            "version": "1.0.0",
            "created": datetime.now(timezone.utc).isoformat(),
            "ssh": self.DEFAULT_CONFIG["ssh"].copy(),
            "git": {
                **self.DEFAULT_CONFIG["git"],
                "user": git_user,
                "email": git_email,
                "author_format": f"{git_user} <{git_email}>",
            },
            "github": self.DEFAULT_CONFIG["github"].copy(),
            "verification": {
                "last_ssh_test": None,
                "last_ssh_success": False,
                "git_config_valid": False,
            },
            "tags": ["ssh", "git", "authentication", "wheel-wide"],
        }
        
        # Generate filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"sshconfig-{timestamp}.lug.json"
        lug_path = self.lugs_dir / filename
        
        # Write lug
        with open(lug_path, 'w') as f:
            json.dump(lug, f, indent=2)
        
        self._config = None  # Clear cache
        return lug_path

    def update_config(self, updates: Dict[str, Any]):
        """
        Update configuration in lug.
        
        Args:
            updates: Dict with ssh, git, or github keys to update
        """
        config = self.load_config()
        
        for key, value in updates.items():
            if key in config and isinstance(config[key], dict):
                config[key].update(value)
        
        # Find lug and update it
        lug_file = self._find_sshconfig_lug()
        if not lug_file:
            raise RuntimeError("No sshconfig lug found. Create one first with create_default_lug().")
        
        # Load, update, save
        with open(lug_file, 'r') as f:
            lug = json.load(f)
        
        for key, value in updates.items():
            if key in lug and isinstance(lug[key], dict):
                lug[key].update(value)
        
        lug["modified"] = datetime.now(timezone.utc).isoformat()
        
        with open(lug_file, 'w') as f:
            json.dump(lug, f, indent=2)
        
        self._config = None  # Clear cache

    def get_ssh_key_path(self) -> str:
        """Get SSH key path, expanding ~ to home directory."""
        config = self.load_config()
        path = config["ssh"]["key_path"]
        return os.path.expanduser(path)

    def get_ssh_verify_command(self) -> str:
        """Get SSH verify command (to test key authentication)."""
        config = self.load_config()
        return config["ssh"]["verify_command"]

    def get_git_user(self) -> str:
        """Get git user name."""
        config = self.load_config()
        return config["git"]["user"]

    def get_git_email(self) -> str:
        """Get git email."""
        config = self.load_config()
        return config["git"]["email"]

    def get_git_author(self) -> str:
        """Get git author format (for commits)."""
        config = self.load_config()
        return config["git"]["author_format"]

    def get_git_default_remote(self) -> str:
        """Get default git remote (usually 'origin')."""
        config = self.load_config()
        return config["git"]["default_remote"]

    def get_git_default_branch(self) -> str:
        """Get default git branch (usually 'main')."""
        config = self.load_config()
        return config["git"]["default_branch"]

    def get_github_host(self) -> str:
        """Get GitHub host."""
        config = self.load_config()
        return config["github"]["host"]

    def get_github_remote_format(self) -> str:
        """Get GitHub remote format template."""
        config = self.load_config()
        return config["github"]["remote_format"]

    def verify_ssh_key_exists(self) -> bool:
        """Check if SSH key file exists."""
        key_path = self.get_ssh_key_path()
        return Path(key_path).exists()

    def verify_git_config(self) -> Dict[str, bool]:
        """
        Verify git configuration.
        
        Returns:
            Dict with verification results
        """
        import subprocess
        
        results = {
            "user_name_set": False,
            "user_email_set": False,
            "ssh_key_exists": self.verify_ssh_key_exists(),
        }
        
        # Check git config
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            results["user_name_set"] = result.returncode == 0
        except:
            pass
        
        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            results["user_email_set"] = result.returncode == 0
        except:
            pass
        
        return results

    def _generate_wheel_id(self) -> str:
        """Generate a random wheel ID."""
        import hashlib
        import uuid
        return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:12]

    def _get_wheel_id(self) -> str:
        """Get wheel ID from WAI-State.json."""
        state_file = Path(self.spoke_path).parent / "WAI-Spoke" / "WAI-State.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    return state.get("wheel", {}).get("spoke_id", "unknown")
            except:
                pass
        return "unknown"


# Module-level functions for convenience
_config = None


def get_config(spoke_path: str = None) -> SSHGitConfig:
    """Get or create global SSH/git config."""
    global _config
    if _config is None:
        _config = SSHGitConfig(spoke_path)
    return _config


def load_ssh_config() -> Dict[str, Any]:
    """Convenience: load SSH/git config."""
    return get_config().load_config()


def get_ssh_key_path() -> str:
    """Convenience: get SSH key path."""
    return get_config().get_ssh_key_path()


def get_git_author() -> str:
    """Convenience: get git author."""
    return get_config().get_git_author()


def get_git_default_branch() -> str:
    """Convenience: get default branch."""
    return get_config().get_git_default_branch()
