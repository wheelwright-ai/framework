"""
CLI Observation Integration - Wire observation logging into all CLI commands.

Every CLI command automatically logs observations for audit trail and session playback.
"""

import os
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timezone
from functools import wraps

from wai.observation import get_logger
from wai.config import get_config


def get_session_id(command_name: str) -> str:
    """Generate session ID for CLI command."""
    return f"cli-{command_name}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"


def with_observations(command_name: str, category: str = "workflow"):
    """
    Decorator to add observation logging to CLI commands.
    
    Usage:
        @with_observations("init", category="workflow")
        def cmd_init(args):
            # Command code
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            session_id = get_session_id(command_name)
            logger = get_logger()
            
            # Log command execution
            plan = f"Execute CLI command: {command_name}"
            command = f"wai {command_name}"
            
            try:
                # Execute command
                result = func(*args, **kwargs)
                
                # Log success
                logger.log_observation(
                    action_id=f"cli.{command_name}",
                    action_category=category,
                    action_description=f"Execute: wai {command_name}",
                    plan=plan,
                    command=command,
                    expected_result={"exit_code": 0},
                    actual_result={
                        "exit_code": 0,
                        "output": str(result)[:200],
                        "status": "success"
                    },
                    verification={
                        "passed": True,
                        "checks": [{"name": "command_executed", "passed": True}]
                    },
                    session_id=session_id,
                    tags=[category, command_name],
                )
                
                return result
                
            except Exception as e:
                # Log failure
                logger.log_observation(
                    action_id=f"cli.{command_name}",
                    action_category=category,
                    action_description=f"Execute: wai {command_name}",
                    plan=plan,
                    command=command,
                    expected_result={"exit_code": 0},
                    actual_result={
                        "exit_code": 1,
                        "error": str(e)[:200],
                        "status": "failed"
                    },
                    verification={
                        "passed": False,
                        "checks": [{"name": "command_executed", "passed": False}]
                    },
                    session_id=session_id,
                    remediation={
                        "issue": f"Command failed: {str(e)[:100]}",
                        "suggested_next_step": f"Check error and retry: wai {command_name}"
                    },
                    tags=[category, command_name, "error"],
                )
                raise
        
        return wrapper
    return decorator


class CLIObservationContext:
    """Context manager for observation logging in CLI commands."""
    
    def __init__(self, command_name: str, category: str = "workflow"):
        """
        Initialize observation context.
        
        Args:
            command_name: Name of CLI command
            category: Category (workflow, git, state, sync)
        """
        self.command_name = command_name
        self.category = category
        self.session_id = get_session_id(command_name)
        self.logger = get_logger()
        self.start_time = None

    def __enter__(self):
        """Start observation context."""
        self.start_time = datetime.now(timezone.utc)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End observation context and log."""
        duration_ms = int((datetime.now(timezone.utc) - self.start_time).total_seconds() * 1000)
        
        if exc_type is None:
            # Success
            self.logger.log_observation(
                action_id=f"cli.{self.command_name}",
                action_category=self.category,
                action_description=f"CLI: {self.command_name}",
                plan=f"Execute command {self.command_name}",
                command=f"wai {self.command_name}",
                expected_result={"exit_code": 0},
                actual_result={
                    "exit_code": 0,
                    "duration_ms": duration_ms,
                    "status": "success"
                },
                verification={
                    "passed": True,
                    "checks": [{"name": "exit_code_zero", "passed": True}]
                },
                session_id=self.session_id,
                tags=[self.category, self.command_name],
            )
        else:
            # Failure
            self.logger.log_observation(
                action_id=f"cli.{self.command_name}",
                action_category=self.category,
                action_description=f"CLI: {self.command_name}",
                plan=f"Execute command {self.command_name}",
                command=f"wai {self.command_name}",
                expected_result={"exit_code": 0},
                actual_result={
                    "exit_code": 1,
                    "error": str(exc_val),
                    "duration_ms": duration_ms,
                    "status": "failed"
                },
                verification={
                    "passed": False,
                    "checks": [{"name": "exit_code_zero", "passed": False}]
                },
                session_id=self.session_id,
                remediation={
                    "issue": f"Command failed: {str(exc_val)[:100]}",
                    "suggested_next_step": f"Check error logs and retry"
                },
                tags=[self.category, self.command_name, "error"],
            )
        
        return False  # Don't suppress exceptions


def ensure_ssh_config_exists():
    """
    Ensure SSH config lug exists.
    
    If no SSH config lug found, create default.
    """
    config = get_config()
    
    # Check if config loads
    config_data = config.load_config()
    
    # If this is a fresh wheel (git user is default), create SSH config
    if config_data["git"]["user"] == "User Name":
        # Create default SSH config
        config.create_default_lug(
            git_user="Wheelwright CLI",
            git_email="cli@wheelwright.ai"
        )
        return True
    
    return False


def log_cli_action(
    action_id: str,
    action_description: str,
    result_success: bool,
    error_msg: str = None,
    command_name: str = "unknown",
) -> Dict[str, Any]:
    """
    Log a CLI action with observation.
    
    Args:
        action_id: Unique action ID (e.g., "cli.init")
        action_description: Human description
        result_success: Whether action succeeded
        error_msg: Error message if failed
        command_name: CLI command name
    
    Returns:
        Observation dict
    """
    logger = get_logger()
    session_id = get_session_id(command_name)
    
    return logger.log_observation(
        action_id=action_id,
        action_category="cli",
        action_description=action_description,
        plan=f"CLI action: {action_description}",
        command=f"wai {command_name}",
        expected_result={"success": True},
        actual_result={
            "success": result_success,
            "error": error_msg if error_msg else None
        },
        verification={
            "passed": result_success,
            "checks": [{"name": "action_succeeded", "passed": result_success}]
        },
        session_id=session_id,
        remediation={
            "issue": error_msg,
            "suggested_next_step": f"Review error and retry"
        } if error_msg else None,
        tags=["cli", command_name],
    )
