#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

lug = {
    'i': 'hub-state-jit-context',
    't': 'feature',
    'ty': 'feature',
    'title': 'Hub Just-In-Time Context - Tool Quotas and Push Notifications',
    's': 'c',
    'status': 'closed',
    'description': 'Implemented complete just-in-time hub context system enabling spokes to receive real-time quota warnings and critical notifications from hub. Features: (1) Tool quota tracking with expiry - generic schema for any tool (AMP, Claude Code, etc.) with auto-cleanup, (2) Push notification system - hub broadcasts critical updates to all spokes, (3) Briefing integration - wai-briefing.sh displays quotas with usage %, time until reset, warning icons, (4) Easy update - WAI hub quota command and Python API. User story: AMP hits quota → user updates hub quota → all spokes see warning on wakeup with countdown. Solves critical awareness gap for IDE quotas and rate limits.',
    'priority': 'high',
    'impact': 10,
    'value': 10,
    'scope': 'framework',
    'modules_affected': ['hub', 'briefing', 'cli'],
    'category': 'feature',
    'subcategory': 'just-in-time-context',
    'tags': ['hub', 'quotas', 'notifications', 'real-time', 'awareness', 'ide-integration'],
    'verify_on_closeout': False,
    'created_at': datetime.now().isoformat(),
    'closed_at': datetime.now().isoformat(),
    'blocks': [],
    'blocked_by': []
}

# Append to lugs file
lugs_file = Path('WAI-Spoke/WAI-Lugs.jsonl')
with open(lugs_file, 'a') as f:
    f.write(json.dumps(lug) + '\n')

print('✓ Lug created: hub-state-jit-context')
