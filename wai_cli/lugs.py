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
        self.deps: List[str] = data.get('deps', [])
        self.blocked_by: List[str] = data.get('blocked_by', [])
        self.policy_tags: List[str] = data.get('policy_tags', [])
        self.origin: Optional[str] = data.get('origin')
        self.resolved_by: Optional[Dict[str, Any]] = data.get('resolved_by')
        self.summary: Optional[str] = data.get('summary')
        self.justification: Optional[str] = data.get('justification')
        self.from_file: Optional[str] = data.get('from_file')
        self.extras: Dict[str, Any] = data.get('extras', {})
    
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
            'duration': self.duration
        }


class LugManager:
    """Manages Lugs with JSONL storage and in-memory indexing."""
    
    def __init__(self, spoke_dir: Path):
        """Initialize LugManager with spoke directory."""
        self.spoke_dir = spoke_dir
        self.lugs_file = spoke_dir / 'lugs.jsonl'
        self.closed_file = spoke_dir / 'lugs-closed.jsonl'
        self.sessions_file = spoke_dir / 'lug-sessions.jsonl'
        
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
                        data = json.loads(line)
                        session = Session(data)
                        self.sessions[session.session_id] = session
    
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
        return hashlib.sha256(content.encode()).hexdigest()[:16]  # 16 chars for readability
    
    def _atomic_append(self, file_path: Path, data: Dict[str, Any]):
        """Atomically append JSON line to file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    def create_lug(
        self,
        title: str,
        lug_type: str = 'work',
        priority: str = 'medium',
        impact: str = 'medium',
        value: int = 5,
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
            'deps': [],
            'blocked_by': [],
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
                with open(self.closed_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            minified = json.loads(line)
                            expanded = self._expand_keys(minified)
                            lug = Lug(expanded)
                            self.closed_lugs[lug.id] = lug
            
            matches = [lug for lug_id, lug in self.closed_lugs.items() if lug_id.startswith(lug_id_prefix)]
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValueError(f"Ambiguous ID prefix '{lug_id_prefix}': matches {len(matches)} Lugs")
        
        return None
    
    def update_lug(
        self,
        lug_id_prefix: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        impact: Optional[str] = None,
        value: Optional[int] = None,
        policy_tags: Optional[List[str]] = None,
        extras: Optional[Dict[str, Any]] = None
    ) -> Lug:
        """
        Update an existing Lug.
        
        Args:
            lug_id_prefix: ID prefix to identify Lug
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
        if status:
            lug.status = status
        if priority:
            lug.priority = priority
        if impact:
            lug.impact = impact
        if value is not None:
            lug.value = value
        if policy_tags is not None:
            lug.policy_tags = list(set(lug.policy_tags + policy_tags))
        if extras:
            lug.extras.update(extras)
        
        lug.updated_at = datetime.now().isoformat()
        
        # Rewrite entire file (TODO: optimize with delta updates)
        self._rewrite_lugs_file()
        
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
        
        # Remove from active
        del self.lugs[lug.id]
        self._rewrite_lugs_file()
        
        return lug
    
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
        
        self._rewrite_lugs_file()
    
    def get_dependency_chain(self, lug_id_prefix: str) -> List[Lug]:
        """Get all dependencies recursively."""
        lug = self.get_lug(lug_id_prefix)
        if not lug:
            return []
        
        visited: Set[str] = set()
        chain: List[Lug] = []
        
        def traverse(current_lug: Lug):
            if current_lug.id in visited:
                return
            visited.add(current_lug.id)
            chain.append(current_lug)
            
            for dep_id in current_lug.deps:
                dep_lug = self.get_lug(dep_id)
                if dep_lug:
                    traverse(dep_lug)
        
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
    
    def _rewrite_lugs_file(self):
        """Rewrite entire lugs.jsonl with current state."""
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
        model: Optional[str] = None
    ) -> Session:
        """Create a new session for attribution."""
        session_data = {
            'session_id': session_id,
            'who': who,
            'ide': ide,
            'timestamp_start': datetime.now().isoformat(),
            'mode': mode,
            'model': model
        }
        
        session = Session(session_data)
        self.sessions[session_id] = session
        self._atomic_append(self.sessions_file, session.to_dict())
        
        return session
