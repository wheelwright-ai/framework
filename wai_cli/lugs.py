"""
Lug System - AI-first task/dependency graph for WAI Framework.

Lugs provide persistent context, memory, and structured tracking so AI
becomes a true force multiplier and responsible partner.

Core features:
- JSONL append-only storage (active/closed separation)
- SHA-256 ID generation with collision resistance
- In-memory indexing for fast queries
- Dependency graph management
- Policy validation hooks
- Minification for storage efficiency
"""

import hashlib
import json
import random
import string
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set


# Minification key mappings (storage → API)
MINIFIED_KEYS = {
    'i': 'id',
    't': 'title',
    'ty': 'type',
    's': 'status',
    'ca': 'created_at',
    'ua': 'updated_at',
    'cla': 'closed_at',
    'p': 'priority',
    'im': 'impact',
    'v': 'value',
    'si': 'session_id',
    'd': 'deps',
    'bb': 'blocked_by',
    'pt': 'policy_tags',
    'o': 'origin',
    'rb': 'resolved_by',
    'su': 'summary',
    'j': 'justification',
    'ff': 'from_file',
    'ex': 'extras'
}

# Reverse mapping (API → storage)
EXPANDED_KEYS = {v: k for k, v in MINIFIED_KEYS.items()}


class Lug:
    """Represents a single Lug (task/issue/bug/work item)."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize Lug from data dict."""
        self.id: str = data['id']
        self.title: str = data['title']
        self.type: str = data['type']
        self.status: str = data['status']
        self.created_at: str = data['created_at']
        self.updated_at: str = data.get('updated_at', self.created_at)
        self.closed_at: Optional[str] = data.get('closed_at')
        self.priority: str = data.get('priority', 'medium')
        self.impact: str = data.get('impact', 'medium')
        self.value: int = data.get('value', 5)
        self.session_id: Optional[str] = data.get('session_id')
        
        # Relationships
        # Defensive: ensure these are always lists, even if None in data
        self.deps: List[str] = data.get('deps') or []
        self.blocked_by: List[str] = data.get('blocked_by') or []
        self.policy_tags: List[str] = data.get('policy_tags') or []
        self.origin: Optional[str] = data.get('origin')
        self.resolved_by: Optional[Dict[str, Any]] = data.get('resolved_by')
        self.summary: Optional[str] = data.get('summary')
        self.justification: Optional[str] = data.get('justification')
        self.from_file: Optional[str] = data.get('from_file')
        self.extras: Dict[str, Any] = data.get('extras') or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to full dict with all fields."""
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'closed_at': self.closed_at,
            'priority': self.priority,
            'impact': self.impact,
            'value': self.value,
            'session_id': self.session_id,
            'deps': self.deps,
            'blocked_by': self.blocked_by,
            'policy_tags': self.policy_tags,
            'origin': self.origin,
            'resolved_by': self.resolved_by,
            'summary': self.summary,
            'justification': self.justification,
            'from_file': self.from_file,
            'extras': self.extras
        }
    
    def to_minified(self) -> Dict[str, Any]:
        """Convert to minified dict for storage."""
        data = self.to_dict()
        minified = {}
        for key, value in data.items():
            if value is not None:  # Omit null fields
                minified[EXPANDED_KEYS.get(key, key)] = value
        return minified


class Session:
    """Represents a session for Lug attribution."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize Session from data dict."""
        self.session_id: str = data['session_id']
        self.who: str = data['who']
        self.ide: str = data['ide']
        self.timestamp_start: str = data['timestamp_start']
        self.timestamp_end: Optional[str] = data.get('timestamp_end')
        self.mode: str = data.get('mode', 'YOLO')
        self.model: Optional[str] = data.get('model')
        self.duration: Optional[float] = data.get('duration')
        
        # Multi-Agent Tracking (Lug 5.1)
        self.agent_id: Optional[str] = data.get('agent_id')
        self.agent_role: Optional[str] = data.get('agent_role')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict."""
        return {
            'session_id': self.session_id,
            'who': self.who,
            'ide': self.ide,
            'timestamp_start': self.timestamp_start,
            'timestamp_end': self.timestamp_end,
            'mode': self.mode,
            'model': self.model,
            'duration': self.duration,
            'agent_id': self.agent_id,
            'agent_role': self.agent_role
        }


class LugManager:
    """Manages Lugs with JSONL storage and in-memory indexing."""
    
    def __init__(self, spoke_dir: Path):
        """Initialize LugManager with spoke directory."""
        self.spoke_dir = spoke_dir
        self.lugs_file = spoke_dir / 'lugs.jsonl'
        self.closed_file = spoke_dir / 'lugs-closed.jsonl'
        self.sessions_file = spoke_dir / 'sessions.jsonl'
        
        # In-memory indices
        self.lugs: Dict[str, Lug] = {}
        self.closed_lugs: Dict[str, Lug] = {}
        self.sessions: Dict[str, Session] = {}
        
        # Load existing data
        self._load_lugs()
        self._load_sessions()
    
    def _load_lugs(self):
        """Load active Lugs from JSONL."""
        if self.lugs_file.exists():
            with open(self.lugs_file, 'r') as f:
                for line in f:
                    if line.strip():
                        minified = json.loads(line)
                        expanded = self._expand_keys(minified)
                        lug = Lug(expanded)
                        self.lugs[lug.id] = lug
    
    def _load_sessions(self):
        """Load sessions from JSONL."""
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            # Only load items that look like full sessions (have 'who')
                            # Beads might be minimal history nodes
                            if 'who' in data:
                                session = Session(data)
                                self.sessions[session.session_id] = session
                        except (json.JSONDecodeError, KeyError):
                            continue
    
    def _expand_keys(self, minified: Dict[str, Any]) -> Dict[str, Any]:
        """Expand minified keys to full field names."""
        expanded = {}
        for key, value in minified.items():
            expanded[MINIFIED_KEYS.get(key, key)] = value
        return expanded
    
    def _generate_id(self, title: str, created_at: str) -> str:
        """Generate SHA-256 ID from title, timestamp, and random salt."""
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        content = f"{title}{created_at}{salt}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _atomic_append(self, file_path: Path, data: Dict[str, Any]):
        """Atomically append JSON line to file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')

    def _get_active_session_id(self) -> Optional[str]:
        """Try to get active session ID from WAI-State.json."""
        try:
            state_file = self.spoke_dir / 'WAI-State.json'
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    return state.get('_session_state', {}).get('current_session', {}).get('session_id')
        except Exception:
            pass
        return None
    
    def create_lug(
        self,
        title: str,
        lug_type: str = 'work',
        priority: str = 'medium',
        impact: str = 'medium',
        value: int = 5,
        session_id: Optional[str] = None,
        deps: Optional[List[str]] = None,
        blocked_by: Optional[List[str]] = None,
        justification: Optional[str] = None,
        origin: Optional[str] = None,
        from_file: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None
    ) -> Lug:
        """
        Create a new Lug.
        
        Args:
            title: Short description
            lug_type: Type (epic, issue, bug, work, ask, or custom)
            priority: Priority level (low, medium, high)
            impact: Impact size (small, medium, large)
            value: Value score 1-10
            justification: Originating request/story
            origin: Source (e.g., "lint_test:flake8", "user_report:chat")
            from_file: Optional file path this relates to
            extras: Custom data
        
        Returns:
            Created Lug instance
        """
        created_at = datetime.now().isoformat()
        lug_id = self._generate_id(title, created_at)

        # Auto-detect session if not provided
        if not session_id:
            session_id = self._get_active_session_id()
        
        lug_data = {
            'id': lug_id,
            'title': title,
            'type': lug_type,
            'status': 'open',
            'created_at': created_at,
            'updated_at': created_at,
            'priority': priority,
            'impact': impact,
            'value': value,
            'session_id': session_id,
            'deps': deps or [],
            'blocked_by': blocked_by or [],
            'policy_tags': [],
            'origin': origin,
            'justification': justification,
            'from_file': from_file,
            'extras': extras or {}
        }
        
        lug = Lug(lug_data)
        self.lugs[lug_id] = lug
        
        # Append to JSONL
        self._atomic_append(self.lugs_file, lug.to_minified())
        
        return lug
    
    def get_lug(self, lug_id_prefix: str, include_closed: bool = False) -> Optional[Lug]:
        """
        Get Lug by ID prefix.
        
        Args:
            lug_id_prefix: Full or partial ID (min 4 chars)
            include_closed: Search closed Lugs too
        
        Returns:
            Lug if found, None otherwise
        """
        # Search active lugs
        matches = [lug for lug_id, lug in self.lugs.items() if lug_id.startswith(lug_id_prefix)]
        
        if not matches and include_closed:
            # Load closed lugs on-demand
            if not self.closed_lugs and self.closed_file.exists():
                try:
                    with open(self.closed_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                minified = json.loads(line)
                                expanded = self._expand_keys(minified)
                                lug = Lug(expanded)
                                self.closed_lugs[lug.id] = lug
                except Exception:
                    # If file is corrupt or empty, handle gracefully
                    pass
            
            matches = [lug for lug_id, lug in self.closed_lugs.items() if lug_id.startswith(lug_id_prefix)]
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValueError(f"Ambiguous ID prefix '{lug_id_prefix}': matches {len(matches)} Lugs")
        
        return None
    
    def get_open_lugs(self) -> List[Lug]:
        """Get all open Lugs."""
        return list(self.lugs.values())

    def get_closed_lugs(self, since_last_shipit: bool = False) -> List[Lug]:
        """
        Get closed Lugs.
        
        Args:
            since_last_shipit: (Placeholder) for session filtering
        """
        # Ensure closed lugs are loaded
        if not self.closed_lugs and self.closed_file.exists():
            with open(self.closed_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            minified = json.loads(line)
                            expanded = self._expand_keys(minified)
                            lug = Lug(expanded)
                            self.closed_lugs[lug.id] = lug
                        except:
                            continue
        return list(self.closed_lugs.values())

    def update_lug(
        self,
        lug_id_prefix: str,
        title: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        impact: Optional[str] = None,
        value: Optional[int] = None,
        deps: Optional[List[str]] = None,
        blocked_by: Optional[List[str]] = None,
        policy_tags: Optional[List[str]] = None,
        extras: Optional[Dict[str, Any]] = None
    ) -> Lug:
        """
        Update an existing Lug.
        
        Args:
            lug_id_prefix: ID prefix to identify Lug
            title: New title
            status: New status
            priority: New priority
            impact: New impact
            value: New value score
            policy_tags: Tags to add/set
            extras: Custom data to merge
        
        Returns:
            Updated Lug
        """
        lug = self.get_lug(lug_id_prefix)
        if not lug:
            raise ValueError(f"No Lug found with ID prefix '{lug_id_prefix}'")
        
        # Update fields
        if title:
            lug.title = title
        if status:
            lug.status = status
        if priority:
            lug.priority = priority
        if impact:
            lug.impact = impact
        if value is not None:
            lug.value = value
        if deps is not None:
            lug.deps = deps
        if blocked_by is not None:
            # Defensive check: ensure list
            if not isinstance(blocked_by, list):
                if isinstance(blocked_by, str):
                    blocked_by = [blocked_by]
                else:
                    blocked_by = list(blocked_by)
            lug.blocked_by = blocked_by
        if policy_tags is not None:
            # Defensive initialization if Lug has None
            current_tags = lug.policy_tags or []
            lug.policy_tags = list(set(current_tags + policy_tags))
        if extras:
            # Check for special session_id update (allows unlinking via extras={'session_id': None})
            if 'session_id' in extras:
                lug.session_id = extras.pop('session_id')
            
            lug.extras.update(extras)
            
        lug.updated_at = datetime.now().isoformat()
        
        # Delta update - only update this lug in file
        self._update_lug_in_file(lug.id)
        
        return lug
    
    def close_lug(
        self,
        lug_id_prefix: str,
        summary: Optional[str] = None,
        resolved_by: Optional[Dict[str, Any]] = None,
        skip_policy_check: bool = False
    ) -> Lug:
        """
        Close a Lug and archive it.
        
        Args:
            lug_id_prefix: ID prefix to identify Lug
            summary: Closing summary
            resolved_by: Resolution attribution
            skip_policy_check: Skip policy validation
        
        Returns:
            Closed Lug
        """
        lug = self.get_lug(lug_id_prefix)
        if not lug:
            raise ValueError(f"No Lug found with ID prefix '{lug_id_prefix}'")
        
        # Check policies
        if not skip_policy_check:
            violations = self.validate_policies(lug)
            if violations:
                raise ValueError(f"Policy violations prevent closing:\n" + "\n".join(violations))
        
        # Update lug
        lug.status = 'closed'
        lug.closed_at = datetime.now().isoformat()
        lug.updated_at = lug.closed_at
        lug.summary = summary
        lug.resolved_by = resolved_by
        
        # Move to closed archive
        self._atomic_append(self.closed_file, lug.to_minified())
        
        # Remove from active using delta removal
        lug_id = lug.id
        del self.lugs[lug_id]
        self._remove_lug_from_file(lug_id)
        
        # Update in-memory closed cache
        self.closed_lugs[lug_id] = lug
        
        return lug
    
    def delete_lug(self, lug_id_prefix: str):
        """
        Permanently delete a Lug.
        """
        lug = self.get_lug(lug_id_prefix, include_closed=True)
        if not lug:
            raise ValueError(f"No Lug found with ID prefix '{lug_id_prefix}'")
            
        lug_id = lug.id
        
        # Remove from memory
        if lug_id in self.lugs:
            del self.lugs[lug_id]
        if lug_id in self.closed_lugs:
            del self.closed_lugs[lug_id]
            
        # Remove from both files to be safe (it's one or the other but this covers it)
        self._remove_lug_from_file(lug_id)
        
        # Also remove from closed file if it was there
        # _remove_lug_from_file uses self.lugs_file, we need to handle closed_file manually or reuse
        # The _remove_lug_from_file implementation is tied to self.lugs_file.
        # Let's make a generic helper or just duplicate logic for safety since I can't refactor everything.
        # Actually _remove_lug_from_file is hardcoded to self.lugs_file.
        # I should just execute the same logic for closed_file.
        
        if self.closed_file.exists():
            temp_file = self.closed_file.with_suffix('.jsonl.tmp')
            with open(self.closed_file, 'r') as src, open(temp_file, 'w') as dst:
                for line in src:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        line_id = data.get('i') or data.get('id')
                        if line_id != lug_id:
                            dst.write(line)
                    except:
                        dst.write(line)
            temp_file.replace(self.closed_file)


    
    def add_dependency(self, lug_id_prefix: str, dep_id_prefix: str):
        """
        Add a dependency relationship.
        
        Args:
            lug_id_prefix: Lug that depends on another
            dep_id_prefix: Dependency Lug
        """
        lug = self.get_lug(lug_id_prefix)
        dep = self.get_lug(dep_id_prefix)
        
        if not lug or not dep:
            raise ValueError("Both Lugs must exist")
        
        if dep.id not in lug.deps:
            lug.deps.append(dep.id)
        
        if lug.id not in dep.blocked_by:
            dep.blocked_by.append(lug.id)
        
        lug.updated_at = datetime.now().isoformat()
        dep.updated_at = lug.updated_at
        
        # Delta updates for both modified lugs
        self._update_lug_in_file(lug.id)
        self._update_lug_in_file(dep.id)
    
    def get_dependency_chain(self, lug_id_prefix: str, max_depth: int = 100) -> List[Lug]:
        """Get all dependencies recursively.
        
        Args:
            lug_id_prefix: ID prefix of starting lug
            max_depth: Maximum recursion depth (prevents infinite loops)
        """
        lug = self.get_lug(lug_id_prefix)
        if not lug:
            return []
        
        visited: Set[str] = set()
        chain: List[Lug] = []
        
        def traverse(current_lug: Lug, depth: int = 0):
            if current_lug.id in visited or depth > max_depth:
                return
            visited.add(current_lug.id)
            chain.append(current_lug)
            
            for dep_id in current_lug.deps:
                dep_lug = self.get_lug(dep_id)
                if dep_lug:
                    traverse(dep_lug, depth + 1)
        
        traverse(lug)
        return chain
    
    def validate_policies(self, lug: Lug) -> List[str]:
        """
        Validate Lug against policies.
        
        Returns:
            List of violation messages (empty if valid)
        """
        violations = []
        
        # Load policies
        policies_file = self.spoke_dir / 'WAI-Policies.json'
        if not policies_file.exists():
            return violations  # No policies defined
        
        with open(policies_file, 'r') as f:
            policies = json.load(f)
        
        lug_policies = policies.get('lug_policies', {})
        type_policy = lug_policies.get(lug.type, {})
        
        # Check close requirements
        required_tags = type_policy.get('close_requires', [])
        for tag in required_tags:
            if tag not in lug.policy_tags:
                violations.append(f"Missing required policy tag: {tag}")
        
        # Add global violations
        violations.extend(self._validate_global_policies(lug))
        
        return violations
    
    def list_lugs(
        self,
        status: Optional[str] = None,
        lug_type: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Lug]:
        """
        List Lugs with optional filters.
        
        Args:
            status: Filter by status
            lug_type: Filter by type
            priority: Filter by priority
        
        Returns:
            Filtered list of Lugs
        """
        lugs = list(self.lugs.values())
        
        if status:
            lugs = [l for l in lugs if l.status == status]
        if lug_type:
            lugs = [l for l in lugs if l.type == lug_type]
        if priority:
            lugs = [l for l in lugs if l.priority == priority]
        
        # Sort by created_at descending
        lugs.sort(key=lambda l: l.created_at, reverse=True)
        
        return lugs
    
    def get_ready_lugs(self, limit: int = 10) -> List[Lug]:
        """
        Get Lugs that are ready to work on (no open dependencies),
        sorted by Priority and Value.
        
        Sorting:
        1. Priority (Critical > High > Medium > Low)
        2. Value (High > Low)
        3. Age (Oldest > Newest)
        """
        # Helper for priority mapping
        def prio_score(p: str) -> int:
            p = str(p).lower()
            if p in ('0', 'critical'): return 0
            if p in ('1', 'high'): return 1
            if p in ('2', 'medium'): return 2
            if p in ('3', 'low'): return 3
            if p in ('4', 'backlog'): return 4
            return 2 # Default to Medium
            
        ready_lugs = []
        open_lugs = self.get_open_lugs()
        
        for lug in open_lugs:
            # Check dependencies
            blocked = False
            for dep_id in (lug.deps or []):
                dep = self.get_lug(dep_id)
                # If dependency exists and is NOT closed, we are blocked
                if dep and dep.status != 'closed':
                    blocked = True
                    break
            
            if not blocked:
                ready_lugs.append(lug)
        
        # Sort
        ready_lugs.sort(key=lambda l: (
            prio_score(l.priority),             # Lower is better (0=Critical)
            -1 * (l.value or 0),                # Higher is better
            l.created_at                        # Older is better (FIFO)
        ))
        
        return ready_lugs[:limit]
    
    def _update_lug_in_file(self, lug_id: str):
        """
        Update a single lug in-place using a temp file for atomicity.
        O(n) read but only for the specific update, not full rewrite.
        """
        if not self.lugs_file.exists():
            return
        
        lug = self.lugs.get(lug_id)
        if not lug:
            return
        
        temp_file = self.lugs_file.with_suffix('.jsonl.tmp')
        found = False
        
        with open(self.lugs_file, 'r') as src, open(temp_file, 'w') as dst:
            for line in src:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    line_id = data.get('i') or data.get('id')
                    if line_id == lug_id:
                        dst.write(json.dumps(lug.to_minified()) + '\n')
                        found = True
                    else:
                        dst.write(line)
                except json.JSONDecodeError:
                    dst.write(line)
        
        if found:
            temp_file.replace(self.lugs_file)
        else:
            temp_file.unlink()
            self._atomic_append(self.lugs_file, lug.to_minified())
    
    def _remove_lug_from_file(self, lug_id: str):
        """
        Remove a single lug from file using a temp file for atomicity.
        """
        if not self.lugs_file.exists():
            return
        
        temp_file = self.lugs_file.with_suffix('.jsonl.tmp')
        
        with open(self.lugs_file, 'r') as src, open(temp_file, 'w') as dst:
            for line in src:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    line_id = data.get('i') or data.get('id')
                    if line_id != lug_id:
                        dst.write(line)
                except json.JSONDecodeError:
                    dst.write(line)
        
        temp_file.replace(self.lugs_file)
    
    def _compact_lugs_file(self):
        """Rewrite entire lugs.jsonl with current state (compaction/fallback)."""
        if self.lugs_file.exists():
            self.lugs_file.unlink()
        
        for lug in self.lugs.values():
            self._atomic_append(self.lugs_file, lug.to_minified())
    
    def create_session(
        self,
        session_id: str,
        who: str,
        ide: str,
        mode: str = 'YOLO',
        model: Optional[str] = None,
        agent_id: Optional[str] = None,
        agent_role: Optional[str] = None
    ) -> Session:
        """Create a new session for attribution."""
        session_data = {
            'session_id': session_id,
            'who': who,
            'ide': ide,
            'timestamp_start': datetime.now().isoformat(),
            'mode': mode,
            'model': model,
            'agent_id': agent_id,
            'agent_role': agent_role
        }
        
        session = Session(session_data)
        self.sessions[session_id] = session
        self._atomic_append(self.sessions_file, session.to_dict())
        
        return session

    def record_session_bead(
        self,
        session_id: str,
        summary: str,
        parent_id: Optional[str] = None,
        files_modified: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Record an immutable session 'bead' (history node).
        
        Args:
            session_id: ID of the session
            summary: Session summary
            parent_id: Hash of the previous session (bead)
            files_modified: List of modified files
            
        Returns:
            The recorded bead dict
        """
        bead = {
            'bead_id': hashlib.sha256(f"{session_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            'session_id': session_id,
            'parent_id': parent_id,
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'files_modified': files_modified or []
        }
        
        self._atomic_append(self.sessions_file, bead)
        return bead

    def get_bead_chain(self) -> List[Dict[str, Any]]:
        """
        Retrieve the full session bead chain, sorted by timestamp.
        
        Returns:
            List of bead dicts
        """
        if not self.sessions_file.exists():
            return []
            
        beads = []
        with open(self.sessions_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if 'bead_id' in data: # Only load beads, skip legacy sessions if mixed
                            beads.append(data)
                    except json.JSONDecodeError:
                        continue
        
        # Sort by timestamp to reconstruct linear history
        # (Though append-only *should* be chronological, this handles async drift)
        beads.sort(key=lambda x: x.get('timestamp', ''))
        return beads

    def validate_bead_chain(self) -> Dict[str, Any]:
        """
        Validate the integrity of the bead chain.
        
        Checks:
        1. Genesis bead (parent_id is None)
        2. Linkage (bead[i].parent_id == bead[i-1].bead_id)
        3. Tampering (re-hashing content matches bead_id - TODO in future)
        
        Returns:
            Dict with 'valid' (bool) and 'errors' (list)
        """
        beads = self.get_bead_chain()
        errors = []
        
        if not beads:
            return {'valid': True, 'errors': [], 'chain_length': 0}

        # Check Genesis
        # First bead in time *usually* has parent_id=None, unless we started recording mid-project
        # So we don't strictly enforce genesis=None for the first file entry, 
        # but we do check that if parent_id exists, the parent is found.
        
        bead_map = {b['bead_id']: b for b in beads}
        
        for i, bead in enumerate(beads):
            parent_id = bead.get('parent_id')
            bead_id = bead.get('bead_id')
            
            # Skip check for genesis-like beads (explicitly no parent)
            if not parent_id:
                continue
                
            # Check if parent exists in our known chain
            if parent_id not in bead_map:
                # This might be valid if the parent is from before we started tracking,
                # or it indicates a broken chain (missing file content).
                # For now, we flag it as a warning/break.
                # Special case: if parent_id looks like a session_id (legacy link), we might accept it 
                # but we can't verify the hash.
                if len(parent_id) != 16: # Assuming our beads are 16 chars
                     # Legacy or custom ID
                     pass
                else:
                    errors.append(f"Broken link: Bead {bead_id[:8]} points to missing parent {parent_id[:8]}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'chain_length': len(beads)
        }

    def is_significant(self, lug: Lug) -> bool:
        """
        Check if a Lug is considered high-significance.
        Criteria: priority=high OR impact=large OR value>=7.
        """
        return (
            lug.priority == 'high' or 
            lug.impact == 'large' or 
            (isinstance(lug.value, (int, float)) and lug.value >= 7)
        )

    def add_policy_type(self, lug_type: str, rules: Dict[str, Any]):
        """
        Add or update a custom Lug type policy.
        """
        policies_file = self.spoke_dir / 'WAI-Policies.json'
        
        if policies_file.exists():
            with open(policies_file, 'r') as f:
                policies = json.load(f)
        else:
            policies = {"lug_policies": {}}
        
        if 'lug_policies' not in policies:
            policies['lug_policies'] = {}
        
        policies['lug_policies'][lug_type] = rules
        
        with open(policies_file, 'w') as f:
            json.dump(policies, f, indent=2)

    def list_lugs_ready_to_close(self) -> List[Lug]:
        """
        List Lugs that pass all policies and are ready to close.
        """
        ready = []
        for lug in self.lugs.values():
            if lug.status != 'open':
                continue
            
            if not self.validate_policies(lug):
                ready.append(lug)
        
        return ready

    def _validate_global_policies(self, lug: Lug) -> List[str]:
        """
        Validate global policies that apply to all Lugs.
        """
        violations = []
        
        # Load policies
        policies_file = self.spoke_dir / 'WAI-Policies.json'
        if not policies_file.exists():
            return violations
        
        with open(policies_file, 'r') as f:
            policies = json.load(f)
        
        global_rules = policies.get('global_policies', [])
        
        for rule in global_rules:
            if rule == "no_open_blockers":
                for dep_id in lug.deps:
                    dep = self.get_lug(dep_id)
                    if dep and dep.status == 'open':
                        violations.append(f"Dependency {dep_id} ({dep.title}) is still open")
            
            elif rule == "no_blocked_by":
                if lug.blocked_by:
                    violations.append(f"This Lug is blocking {len(lug.blocked_by)} other Lugs")
        
        return violations

    def get_session_lugs(self, session_id: str) -> List[Lug]:
        """
        Get all Lugs associated with a specific session.
        
        Checks both lug.session_id and lug.extras['session_id'] for compatibility.
        """
        return [
            l for l in self.lugs.values() 
            if l.session_id == session_id or l.extras.get('session_id') == session_id
        ]

    def infer_lugs_from_git(self, repo: Any) -> List[Dict[str, Any]]:
        """
        Infer possible Lugs from staged git changes.
        """
        suggestions = []
        
        try:
            # Get staged diffs
            diff_index = repo.index.diff("HEAD")
            
            for diff in diff_index:
                # Check if file name indicates a python file
                if not str(diff.a_path).endswith('.py'):
                    continue
                    
                path = Path(diff.a_path)
                try:
                    # diff.diff might be empty or blob
                    content = diff.diff.decode('utf-8', errors='ignore') if diff.diff else ""
                except Exception:
                    content = ""
                
                # Look for TODOs
                todos = re.findall(r'#\s*TODO:?\s*(.*)', content, re.IGNORECASE)
                for todo in todos:
                    suggestions.append({
                        'title': todo.strip(),
                        'type': 'task',
                        'priority': 'medium',
                        'reason': f"Found TODO in {path.name}",
                        'from_file': str(path)
                    })
                    
                # Look for deleted tests
                if "test_" in content and content.startswith('-'):
                    suggestions.append({
                        'title': f"Verify regression for {path.name} (tests modified)",
                        'type': 'bug',
                        'priority': 'high',
                        'reason': f"Test removal detected in {path.name}",
                        'from_file': str(path)
                    })
                    
        except Exception:
            pass
            
        return suggestions
