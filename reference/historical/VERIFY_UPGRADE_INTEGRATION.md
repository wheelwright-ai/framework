# verify-upgrade Command Integration

## Summary

Successfully integrated the `verify-upgrade` command into the WAI CLI framework. The command verifies upgrade-adoption-plan.json on the current spoke.

## Changes Made

### 1. Argument Parser (wai/core.py, lines 431-434)

Added parser definition for the `verify-upgrade` command:
- **Positional argument**: `path` (optional, defaults to current directory)
- **Optional argument**: `--hub-key` (for signature verification)
- **Help text**: "Verify upgrade-adoption-plan.json on current spoke"

```python
# Verify-upgrade command
verify_upgrade_parser = subparsers.add_parser('verify-upgrade', help='Verify upgrade-adoption-plan.json on current spoke')
verify_upgrade_parser.add_argument('path', nargs='?', default='.', help='Project path (default: current directory)')
verify_upgrade_parser.add_argument('--hub-key', help='Hub key for signature verification')
```

### 2. Command Dispatch (wai/core.py, lines 2725-2726)

Added command dispatch in the run() method:

```python
elif args.command == 'verify-upgrade':
    self._cmd_verify_upgrade(args)
```

### 3. Command Handler (wai/core.py, lines 3754-3779)

Added the `_cmd_verify_upgrade` method:

**Features:**
- Parses command arguments (path and hub-key)
- Validates that the spoke is initialized
- Calls `verify_upgrade_command()` from `wai/commands/verify_upgrade.py`
- Returns exit code 0 on success, 1 on failure
- Includes error handling and detailed error messages

```python
def _cmd_verify_upgrade(self, args):
    """Handle verify-upgrade command."""
    from .commands.verify_upgrade import verify_upgrade_command

    try:
        raw_path = getattr(args, 'path', '.')
        spoke_path = normalize_path(raw_path)
        hub_key = getattr(args, 'hub_key', None)

        # Check if spoke exists
        if not check_spoke_initialized(spoke_path):
            print_error(f"No spoke found at {spoke_path}")
            print_info("Run 'WAI init' to initialize a spoke first.")
            sys.exit(1)

        # Run verify-upgrade command
        success = verify_upgrade_command(spoke_path, hub_key)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except Exception as e:
        print_error(f"Verify-upgrade failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

## Pattern Following

The implementation follows the same pattern as other CLI commands:
- Similar to `closeout`, `sync`, and `status` commands
- Uses `normalize_path()` for path handling
- Uses `check_spoke_initialized()` to validate spoke exists
- Imports the command function from `wai/commands/`
- Returns appropriate exit codes (0 for success, 1 for failure)
- Includes error handling with traceback printing

## Usage Examples

### Basic verification
```bash
WAI verify-upgrade
```

### Verify specific project path
```bash
WAI verify-upgrade /path/to/project
```

### Verify with hub signature verification
```bash
WAI verify-upgrade --hub-key my-hub-key
```

### Verify specific path with hub key
```bash
WAI verify-upgrade /path/to/project --hub-key my-hub-key
```

### Show help
```bash
WAI verify-upgrade --help
```

## Help Output

```
usage: WAI verify-upgrade [-h] [--hub-key HUB_KEY] [path]

positional arguments:
  path               Project path (default: current directory)

options:
  -h, --help         show this help message and exit
  --hub-key HUB_KEY  Hub key for signature verification
```

## Exit Codes

- **0**: Verification successful
- **1**: Verification failed or error occurred

## Files Modified

- `wai/core.py`: Added parser, dispatch, and handler for verify-upgrade command

## Files NOT Modified (already exist)

- `wai/commands/verify_upgrade.py`: Contains the actual verification logic
- `wai/upgrade_adoption.py`: Contains helper functions for upgrade plan handling

## Testing

All integration tests pass:
- ✓ Command parser works correctly
- ✓ Handler method exists and is callable
- ✓ Handler has proper docstring
- ✓ Handler imports verify_upgrade_command
- ✓ Handler extracts arguments correctly
- ✓ Handler calls verify_upgrade_command with correct arguments
- ✓ Handler uses proper exit codes (0 for success, 1 for failure)
- ✓ Handler has error handling
- ✓ Handler checks if spoke is initialized
- ✓ Command registered in parser
- ✓ Command in dispatch chain
- ✓ Handler called from dispatch
- ✓ Help text displays correctly

## Verification

To verify the integration works:

```bash
# Test help
python WAI verify-upgrade --help

# Test with non-existent path (should error gracefully)
python WAI verify-upgrade /nonexistent/path
```

Both commands execute successfully with appropriate messages and exit codes.
