"""
Multi-environment session management for Wheelwright.

Enables parallel AI work across multiple tools and machines without collision.
Each environment gets its own session log for tracking and later reconciliation.

Environment = Tool + Machine (e.g., "claude-code-mario-laptop")
"""

import json
import os
import platform
import socket
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List


def detect_environment() -> Dict[str, Any]:
    """
    Auto-detect the current environment (tool, machine, OS).

    Returns:
        Dict with environment details
    """
    # Detect tool from environment variables or process hints
    tool = _detect_tool()

    # Get machine identifier
    machine = _get_machine_id()
    hostname = socket.gethostname()

    # Detect OS details
    os_info = _detect_os()

    # Get working directory
    cwd = os.getcwd()

    # Check for parent session (spawned agent)
    parent_session = os.environ.get('WAI_PARENT_SESSION')

    return {
        'tool': tool['name'],
        'tool_version': tool.get('version'),
        'tool_detected_by': tool.get('detected_by'),
        'machine': machine,
        'hostname': hostname,
        'os': os_info['os'],
        'os_detail': os_info['detail'],
        'cwd': cwd,
        'parent_session': parent_session,
        'is_child_agent': parent_session is not None
    }


def _detect_tool() -> Dict[str, Any]:
    """Detect which AI tool is running."""

    # Claude Code detection
    if os.environ.get('CLAUDE_CODE') or os.environ.get('ANTHROPIC_API_KEY'):
        # Check for child agent
        if os.environ.get('CLAUDE_CODE_AGENT_ID'):
            return {
                'name': 'claude-code-agent',
                'version': os.environ.get('CLAUDE_CODE_VERSION'),
                'detected_by': 'env:CLAUDE_CODE_AGENT_ID'
            }
        return {
            'name': 'claude-code',
            'version': os.environ.get('CLAUDE_CODE_VERSION'),
            'detected_by': 'env:CLAUDE_CODE'
        }

    # Cursor detection
    if os.environ.get('CURSOR_SESSION') or 'cursor' in os.environ.get('TERM_PROGRAM', '').lower():
        return {
            'name': 'cursor',
            'version': os.environ.get('CURSOR_VERSION'),
            'detected_by': 'env:CURSOR_SESSION'
        }

    # VS Code with Copilot
    if os.environ.get('VSCODE_GIT_IPC_HANDLE') or os.environ.get('TERM_PROGRAM') == 'vscode':
        return {
            'name': 'vscode-copilot',
            'version': os.environ.get('VSCODE_VERSION'),
            'detected_by': 'env:VSCODE'
        }

    # Codex CLI
    if os.environ.get('CODEX_CLI'):
        return {
            'name': 'codex',
            'version': os.environ.get('CODEX_VERSION'),
            'detected_by': 'env:CODEX_CLI'
        }

    # ChatGPT web (set by user or bootstrap)
    if os.environ.get('WAI_TOOL') == 'chatgpt':
        return {
            'name': 'chatgpt-web',
            'version': None,
            'detected_by': 'env:WAI_TOOL'
        }

    # Generic web LLM
    if os.environ.get('WAI_TOOL'):
        return {
            'name': os.environ.get('WAI_TOOL'),
            'version': None,
            'detected_by': 'env:WAI_TOOL'
        }

    # Fallback: unknown tool
    return {
        'name': 'unknown',
        'version': None,
        'detected_by': 'fallback'
    }


def _get_machine_id() -> str:
    """Get a friendly machine identifier."""
    # Check for explicit machine name
    if os.environ.get('WAI_MACHINE'):
        return os.environ.get('WAI_MACHINE')

    # Use hostname, cleaned up
    hostname = socket.gethostname().lower()

    # Remove common suffixes
    for suffix in ['.local', '.lan', '.home']:
        if hostname.endswith(suffix):
            hostname = hostname[:-len(suffix)]

    # Shorten long Windows hostnames
    if len(hostname) > 20:
        hostname = hostname[:15]

    return hostname


def _detect_os() -> Dict[str, str]:
    """Detect OS details including WSL."""
    system = platform.system().lower()

    # Check for WSL
    if system == 'linux':
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'microsoft' in version_info or 'wsl' in version_info:
                    return {
                        'os': 'linux/wsl',
                        'detail': 'WSL2' if 'wsl2' in version_info else 'WSL'
                    }
        except:
            pass
        return {'os': 'linux', 'detail': platform.release()}

    if system == 'darwin':
        return {'os': 'macos', 'detail': platform.mac_ver()[0]}

    if system == 'windows':
        return {'os': 'windows', 'detail': platform.release()}

    return {'os': system, 'detail': platform.release()}


def get_session_filename(env: Dict[str, Any]) -> str:
    """
    Generate session filename from environment.

    Format: {tool}-{machine}.jsonl
    Child agents: {tool}-{machine}-{agent_id}.jsonl
    """
    tool = env['tool'].replace(' ', '-').lower()
    machine = env['machine'].replace(' ', '-').lower()

    if env.get('is_child_agent') and env.get('parent_session'):
        # Include agent ID for child agents
        agent_id = hashlib.md5(env['parent_session'].encode()).hexdigest()[:8]
        return f"{tool}-{machine}-child-{agent_id}.jsonl"

    return f"{tool}-{machine}.jsonl"


class MultiEnvSessionManager:
    """
    Manages sessions across multiple environments.

    Each environment gets its own session log in WAI-Spoke/sessions/
    allowing parallel work without collision.
    """

    def __init__(self, spoke_dir: Path):
        """Initialize multi-environment session manager."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'
        self.sessions_dir = self.wai_spoke_dir / 'sessions'
        self.state_file = self.wai_spoke_dir / 'WAI-State.json'

        # Detect current environment
        self.env = detect_environment()
        self.session_filename = get_session_filename(self.env)
        self.session_file = self.sessions_dir / self.session_filename

        # Session state
        self.session_id: Optional[str] = None
        self.started_at: Optional[datetime] = None

    def ensure_sessions_dir(self) -> Path:
        """Ensure sessions directory exists."""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        return self.sessions_dir

    def generate_session_id(self) -> str:
        """Generate unique session ID including environment info."""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        env_hash = hashlib.md5(
            f"{self.env['tool']}{self.env['machine']}".encode()
        ).hexdigest()[:6]
        return f"{self.env['tool']}-{self.env['machine']}-{timestamp}-{env_hash}"

    def start_session(self, ai_name: str = "Claude") -> Dict[str, Any]:
        """
        Start a new session for current environment.

        Writes environment metadata entry to session file.
        """
        self.ensure_sessions_dir()

        self.session_id = self.generate_session_id()
        self.started_at = datetime.now()

        # Check integrations
        integrations = self._check_integrations()

        # Write environment metadata entry
        env_entry = {
            'type': 'env',
            'ts': self.started_at.isoformat(),
            'session_id': self.session_id,
            'tool': self.env['tool'],
            'tool_version': self.env.get('tool_version'),
            'machine': self.env['machine'],
            'hostname': self.env['hostname'],
            'os': self.env['os'],
            'os_detail': self.env.get('os_detail'),
            'cwd': self.env['cwd'],
            'parent_session': self.env.get('parent_session'),
            'integrations': integrations,
            'reconciled': False
        }

        self._append_entry(env_entry)

        return {
            'session_id': self.session_id,
            'session_file': str(self.session_file),
            'environment': self.env,
            'integrations': integrations
        }

    def _check_integrations(self) -> Dict[str, Any]:
        """Check what integrations are available."""
        state = self._load_state()
        hub_path = state.get('wheelwright', {}).get('hub_path')

        return {
            'hub_connected': hub_path is not None and Path(hub_path).exists() if hub_path else False,
            'hub_path': hub_path,
            'git': (self.spoke_dir / '.git').exists(),
            'can_spawn_agents': self.env['tool'] in ['claude-code', 'codex']
        }

    def log_turn(self, role: str, summary: str, metadata: Optional[Dict] = None) -> None:
        """
        Log a conversation turn to environment session file.

        Args:
            role: 'user' or 'assistant'
            summary: Brief summary of the turn (not full content)
            metadata: Optional additional data
        """
        if not self.session_id:
            return

        entry = {
            'type': 'turn',
            'ts': datetime.now().isoformat(),
            'session_id': self.session_id,
            'role': role,
            'summary': summary[:500],  # Limit summary length
            'reconciled': False,
            **(metadata or {})
        }

        self._append_entry(entry)

    def log_decision(self, decision: str, rationale: str, impact: int) -> None:
        """Log a high-impact decision."""
        if not self.session_id:
            return

        entry = {
            'type': 'decision',
            'ts': datetime.now().isoformat(),
            'session_id': self.session_id,
            'decision': decision,
            'rationale': rationale,
            'impact': impact,
            'reconciled': False
        }

        self._append_entry(entry)

    def _append_entry(self, entry: Dict[str, Any]) -> None:
        """Append entry to session file (atomic line write)."""
        self.ensure_sessions_dir()
        with open(self.session_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_session_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent entries from current environment's session file."""
        if not self.session_file.exists():
            return []

        entries = []
        with open(self.session_file, 'r') as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return entries[-limit:]

    def get_all_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all session files and their recent entries.

        Returns:
            Dict mapping session filename to list of entries
        """
        if not self.sessions_dir.exists():
            return {}

        sessions = {}
        for session_file in self.sessions_dir.glob('*.jsonl'):
            entries = []
            with open(session_file, 'r') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            sessions[session_file.name] = entries[-20:]  # Last 20 per file

        return sessions

    def get_cross_session_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary of all environments for cross-session awareness.

        Returns list of environment summaries for display during wakeup.
        """
        all_sessions = self.get_all_sessions()
        summaries = []

        for filename, entries in all_sessions.items():
            # Find most recent env entry
            env_entries = [e for e in entries if e.get('type') == 'env']
            if not env_entries:
                continue

            latest_env = env_entries[-1]

            # Count turns and decisions
            turns = len([e for e in entries if e.get('type') == 'turn'])
            decisions = len([e for e in entries if e.get('type') == 'decision'])
            unreconciled = len([e for e in entries if not e.get('reconciled')])

            # Get last activity
            last_ts = entries[-1].get('ts') if entries else None

            summaries.append({
                'filename': filename,
                'tool': latest_env.get('tool'),
                'machine': latest_env.get('machine'),
                'os': latest_env.get('os'),
                'last_session_id': latest_env.get('session_id'),
                'last_activity': last_ts,
                'total_turns': turns,
                'total_decisions': decisions,
                'unreconciled_entries': unreconciled,
                'is_current': filename == self.session_filename,
                'hub_connected': latest_env.get('integrations', {}).get('hub_connected', False)
            })

        return sorted(summaries, key=lambda x: x.get('last_activity') or '', reverse=True)

    def reconcile_sessions(self, archive_days: int = 30) -> Dict[str, Any]:
        """
        Reconcile all session files during closeout.

        - Mark entries as reconciled
        - Extract decisions to WAI-State.json
        - Update environments registry
        - Prune old reconciled entries

        Returns:
            Dict with reconciliation results
        """
        results = {
            'sessions_processed': 0,
            'entries_reconciled': 0,
            'decisions_extracted': 0,
            'entries_pruned': 0,
            'environments_updated': []
        }

        if not self.sessions_dir.exists():
            return results

        state = self._load_state()

        # Ensure environments registry exists
        if 'environments' not in state:
            state['environments'] = {}

        cutoff_date = datetime.now() - timedelta(days=archive_days)

        for session_file in self.sessions_dir.glob('*.jsonl'):
            entries = []
            kept_entries = []

            with open(session_file, 'r') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            results['sessions_processed'] += 1

            for entry in entries:
                entry_ts = entry.get('ts')
                entry_date = datetime.fromisoformat(entry_ts) if entry_ts else None

                # Extract decisions to state
                if entry.get('type') == 'decision' and not entry.get('reconciled'):
                    impact = entry.get('impact', 0)
                    if impact >= 8:
                        decision_record = {
                            'date': entry_ts[:10] if entry_ts else datetime.now().strftime('%Y-%m-%d'),
                            'decision': entry.get('decision'),
                            'rationale': entry.get('rationale'),
                            'impact': impact,
                            'by': f"{entry.get('session_id', 'unknown')}"
                        }
                        state.setdefault('decisions', []).append(decision_record)
                        results['decisions_extracted'] += 1

                # Update environment registry from env entries
                if entry.get('type') == 'env' and not entry.get('reconciled'):
                    env_key = f"{entry.get('tool')}-{entry.get('machine')}"
                    state['environments'][env_key] = {
                        'tool': entry.get('tool'),
                        'machine': entry.get('machine'),
                        'hostname': entry.get('hostname'),
                        'os': entry.get('os'),
                        'last_seen': entry.get('ts'),
                        'hub_connected': entry.get('integrations', {}).get('hub_connected', False),
                        'last_session_id': entry.get('session_id')
                    }
                    results['environments_updated'].append(env_key)

                # Mark as reconciled
                if not entry.get('reconciled'):
                    entry['reconciled'] = True
                    entry['reconciled_at'] = datetime.now().isoformat()
                    results['entries_reconciled'] += 1

                # Prune old reconciled entries
                if entry.get('reconciled') and entry_date and entry_date < cutoff_date:
                    results['entries_pruned'] += 1
                    continue  # Don't keep this entry

                kept_entries.append(entry)

            # Write back session file with reconciled entries
            with open(session_file, 'w') as f:
                for entry in kept_entries:
                    f.write(json.dumps(entry) + '\n')

        # Save updated state
        self._save_state(state)

        return results

    def _load_state(self) -> Dict[str, Any]:
        """Load WAI-State.json."""
        if not self.state_file.exists():
            return {}
        with open(self.state_file, 'r') as f:
            return json.load(f)

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save WAI-State.json."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        f.write('\n')
