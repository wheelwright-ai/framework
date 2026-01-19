"""
Multi-environment session management for Wheelwright.

Enables parallel AI work across multiple tools and machines without collision.
Each environment gets its own session log for tracking and later reconciliation.

Environment = Tool + Machine (e.g., "claude-code-mario-laptop")

This module handles CROSS-ENVIRONMENT session coordination:
- Summary-only logging (not full content) for lightweight tracking
- Session reconciliation during closeout to merge parallel work
- Environment detection and conflict prevention

Contrast with session.py which handles SINGLE-ENVIRONMENT management
with full content logging and token capacity tracking.
"""

import json
import os
import platform
import socket
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Iterator, Generator

from wai_cli.utils.jsonl import stream_jsonl, stream_jsonl_tail


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

    MAX_SESSION_FILE_SIZE = 1024 * 1024  # 1MB default
    MAX_ACTIVE_ENTRIES = 1000  # Keep last N entries in active file

    def __init__(self, spoke_dir: Path):
        """Initialize multi-environment session manager."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'
        self.sessions_dir = self.wai_spoke_dir / 'sessions'
        self.archive_dir = self.sessions_dir / 'archive'
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

    def get_session_history(self, limit: int = 50, stream: bool = False) -> List[Dict[str, Any]] | Iterator[Dict[str, Any]]:
        """
        Get recent entries from current environment's session file.
        
        Args:
            limit: Maximum number of entries to return
            stream: If True, return an iterator instead of loading all into memory
            
        Returns:
            List of entries (default) or iterator if stream=True
        """
        if not self.session_file.exists():
            return iter([]) if stream else []

        if stream:
            return stream_jsonl_tail(self.session_file, limit)
        
        return list(stream_jsonl_tail(self.session_file, limit))

    def iter_all_sessions(self, limit_per_file: int = 20) -> Generator[tuple[str, Iterator[Dict[str, Any]]], None, None]:
        """
        Iterate over all session files with streaming entries.
        
        Memory-efficient generator that yields (filename, entries_iterator) tuples.
        
        Args:
            limit_per_file: Maximum entries to yield per file
            
        Yields:
            Tuples of (filename, entries_iterator)
        """
        if not self.sessions_dir.exists():
            return

        for session_file in self.sessions_dir.glob('*.jsonl'):
            yield (session_file.name, stream_jsonl_tail(session_file, limit_per_file))

    def get_all_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all session files and their recent entries.

        Returns:
            Dict mapping session filename to list of entries
        """
        return {
            filename: list(entries)
            for filename, entries in self.iter_all_sessions(limit_per_file=20)
        }

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
            'environments_updated': [],
            'archives_created': []
        }

        if not self.sessions_dir.exists():
            return results

        state = self._load_state()

        # Ensure environments registry exists
        if 'environments' not in state:
            state['environments'] = {}

        cutoff_date = datetime.now() - timedelta(days=archive_days)

        for session_file in self.sessions_dir.glob('*.jsonl'):
            kept_entries = []
            results['sessions_processed'] += 1

            for entry in stream_jsonl(session_file):
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

            # Check if archiving is needed for this session file
            archive_result = self.archive_old_entries(session_file)
            if archive_result['archived']:
                results['archives_created'].append(archive_result)

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

    def archive_old_entries(self, session_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Archive old reconciled entries if session file exceeds size limit.

        Args:
            session_file: Specific file to archive, or current session file if None

        Returns:
            Dict with archiving results
        """
        target_file = session_file or self.session_file
        results = {
            'archived': False,
            'entries_archived': 0,
            'archive_file': None,
            'file_size_before': 0,
            'file_size_after': 0
        }

        if not target_file.exists():
            return results

        file_size = target_file.stat().st_size
        results['file_size_before'] = file_size

        if file_size <= self.MAX_SESSION_FILE_SIZE:
            return results

        self.archive_dir.mkdir(parents=True, exist_ok=True)

        all_entries = list(stream_jsonl(target_file))
        total_entries = len(all_entries)

        if total_entries <= self.MAX_ACTIVE_ENTRIES:
            results['file_size_after'] = file_size
            return results

        entries_to_archive = all_entries[:-self.MAX_ACTIVE_ENTRIES]
        entries_to_keep = all_entries[-self.MAX_ACTIVE_ENTRIES:]

        archive_date = datetime.now().strftime('%Y%m%d-%H%M%S')
        archive_filename = f"{target_file.stem}.{archive_date}.jsonl"
        archive_path = self.archive_dir / archive_filename

        with open(archive_path, 'w') as f:
            for entry in entries_to_archive:
                f.write(json.dumps(entry) + '\n')

        with open(target_file, 'w') as f:
            for entry in entries_to_keep:
                f.write(json.dumps(entry) + '\n')

        results['archived'] = True
        results['entries_archived'] = len(entries_to_archive)
        results['archive_file'] = str(archive_path)
        results['file_size_after'] = target_file.stat().st_size

        return results

    def get_archive_files(self, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List archived session files.

        Args:
            pattern: Optional glob pattern to filter archives (e.g., "claude-code-*")

        Returns:
            List of dicts with archive file info
        """
        if not self.archive_dir.exists():
            return []

        glob_pattern = f"{pattern}.*.jsonl" if pattern else "*.jsonl"
        archives = []

        for archive_file in self.archive_dir.glob(glob_pattern):
            stat = archive_file.stat()
            archives.append({
                'filename': archive_file.name,
                'path': str(archive_file),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })

        return sorted(archives, key=lambda x: x['modified'], reverse=True)
