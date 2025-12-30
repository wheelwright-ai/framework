# Wheelwright Hooks

This directory contains Claude Code hooks that enhance the Wheelwright experience.

## session-start.sh

Automatically briefs the user and initializes conversation logging when Claude Code starts a new session.

### What it does

1. **Checks for existing protocol run** - Exits silently if briefing already provided this session
2. **Loads project context** - Reads WAI-State.json for project details
3. **Generates briefing** - Shows:
   - Project name and current phase
   - Last session information
   - Recent high-impact decisions (impact >= 8, up to 3)
   - Next actions (up to 5)
   - Uncommitted changes warning (if applicable)
4. **Initializes conversation logging** - Sets up `.WAI/session-conversation.jsonl` for the new session
5. **Updates session state** - Marks protocol as completed and initializes `current_session` tracking

### Configuration

This hook is automatically triggered by `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.WAI/hooks/session-start.sh"
          }
        ]
      }
    ]
  }
}
```

### Requirements

- **jq** - JSON processor (for reading WAI-State.json)
- **git** - For detecting uncommitted changes
- **bash** - Shell interpreter

### Testing

A comprehensive test suite is provided in `test-session-start.sh`.

#### Running tests

```bash
./.WAI/hooks/test-session-start.sh
```

#### Test coverage

The test suite includes 26 tests across 9 scenarios:

1. **Exit conditions**
   - Exits silently when no .WAI/WAI-State.json exists
   - Exits early when protocol already completed

2. **Briefing generation**
   - Generates correct briefing message with all required sections
   - Includes project name, phase, and session info

3. **Decision filtering**
   - Shows only high-impact decisions (impact >= 8)
   - Limits to 3 most recent decisions
   - Excludes low-impact decisions

4. **Next actions**
   - Shows up to 5 next actions
   - Properly limits list

5. **Git integration**
   - Detects uncommitted changes
   - Lists uncommitted files

6. **Clean state**
   - Shows "Working tree clean" when no changes

7. **State updates**
   - Sets protocol_completed to true
   - Sets briefing_provided to true
   - Adds protocol_last_run timestamp

8. **Error handling**
   - Handles missing optional fields gracefully
   - Works with minimal state files

#### Test output

```
Running session-start.sh tests...

Test: Exit silently when .WAI/WAI-State.json doesn't exist
✓ Should exit with code 0
✓ Should produce no output (empty string)

...

========================================
All tests passed!
Tests run: 26
Passed: 26
========================================
```

### Troubleshooting

#### Hook doesn't run

1. **Check jq is installed**: `which jq`
2. **Check file is executable**: `ls -l .WAI/hooks/session-start.sh`
3. **Check line endings**: File must have Unix (LF) line endings, not Windows (CRLF)
   - Fix: `sed -i 's/\r$//' .WAI/hooks/session-start.sh`

#### Protocol runs every time

If the briefing appears on every message instead of just session start:
- The hook might not be updating the state file correctly
- Check file permissions on `.WAI/WAI-State.json`
- Verify jq can write to the file

#### No briefing appears

1. Verify `.claude/settings.json` exists and has SessionStart hook configured
2. Check hook script has correct shebang: `#!/bin/bash`
3. Run hook manually to test: `CLAUDE_PROJECT_DIR=. ./.WAI/hooks/session-start.sh`

---

## Development

### Adding new hooks

1. Create script in `.WAI/hooks/`
2. Make it executable: `chmod +x .WAI/hooks/your-hook.sh`
3. Add configuration to `.claude/settings.json`
4. Write tests in `test-your-hook.sh`
5. Document in this README

### Hook best practices

- **Exit gracefully**: Use `exit 0` for success, even if nothing to do
- **Check dependencies**: Verify required tools exist before using
- **Handle missing data**: Don't fail on missing optional fields
- **Update state carefully**: Use atomic operations (temp file + mv)
- **Test thoroughly**: Cover happy path and error cases

---

*Wheelwright Framework - wheelwright.ai - MIT License*
