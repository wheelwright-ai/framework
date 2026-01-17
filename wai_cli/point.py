"""
WAI-Point.json - Minimal bootstrap file for quick context restoration.

Provides lightweight entry point with essentials:
- Project summary
- Open Lugs summary
- Last shipit timestamp
- Key learnings

Updated on shipit, can be ingested from seed/ingest/ during closeout.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class PointManager:
    """Manages WAI-Point.json bootstrap file."""
    
    def __init__(self, spoke_dir: Path):
        """Initialize PointManager with spoke directory."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'
        self.point_file = self.wai_spoke_dir / 'WAI-Point.json'
        self.state_file = self.wai_spoke_dir / 'WAI-State.json'
    
    def generate_point(self) -> Dict[str, Any]:
        """
        Generate WAI-Point from current state and Lugs.
        
        Returns:
            Point data dict
        """
        point = {
            'version': '1.0.0',
            'generated_at': datetime.now().isoformat(),
            'summary': '',
            'open_lugs_summary': '',
            'last_shipit': None,
            'key_learnings': []
        }
        
        # Load state
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            # Extract project summary
            wheel = state.get('wheel', {})
            hub = state.get('hub', {})
            point['summary'] = wheel.get('description') or hub.get('summary', '')
            
            # Extract last shipit info
            session_state = state.get('_session_state', {})
            last_closeout = session_state.get('last_closeout', {})
            if last_closeout:
                point['last_shipit'] = {
                    'timestamp': last_closeout.get('closed_at'),
                    'summary': last_closeout.get('summary'),
                    'key_topics': last_closeout.get('key_topics', [])
                }
            
            # Extract key learnings from insights
            context = state.get('context', {})
            insights = context.get('insights', [])
            point['key_learnings'] = insights[:5]  # Top 5
        
        # Load open Lugs summary
        lugs_file = self.wai_spoke_dir / 'lugs.jsonl'
        if lugs_file.exists():
            open_lugs = []
            with open(lugs_file, 'r') as f:
                for line in f:
                    if line.strip():
                        lug_data = json.loads(line)
                        # Expand minified keys if needed
                        from .lugs import MINIFIED_KEYS
                        expanded = {}
                        for key, value in lug_data.items():
                            expanded[MINIFIED_KEYS.get(key, key)] = value
                        
                        open_lugs.append({
                            'type': expanded.get('type'),
                            'priority': expanded.get('priority'),
                            'title': expanded.get('title')
                        })
            
            if open_lugs:
                # Group by priority
                high = [l for l in open_lugs if l['priority'] == 'high']
                medium = [l for l in open_lugs if l['priority'] == 'medium']
                low = [l for l in open_lugs if l['priority'] == 'low']
                
                summary_parts = []
                if high:
                    summary_parts.append(f"{len(high)} high priority")
                if medium:
                    summary_parts.append(f"{len(medium)} medium priority")
                if low:
                    summary_parts.append(f"{len(low)} low priority")
                
                point['open_lugs_summary'] = f"{len(open_lugs)} open Lugs: " + ", ".join(summary_parts)
            else:
                point['open_lugs_summary'] = "No open Lugs"
        else:
            point['open_lugs_summary'] = "No Lugs system initialized"
        
        return point
    
    def update_point(self, shipit_summary: Optional[str] = None):
        """
        Update WAI-Point.json with latest state.
        
        Args:
            shipit_summary: Optional shipit summary to include
        """
        point = self.generate_point()
        
        if shipit_summary:
            if not point['last_shipit']:
                point['last_shipit'] = {}
            point['last_shipit']['timestamp'] = datetime.now().isoformat()
            point['last_shipit']['summary'] = shipit_summary
        
        # Write Point
        with open(self.point_file, 'w') as f:
            json.dump(point, f, indent=2)
    
    def load_point(self) -> Optional[Dict[str, Any]]:
        """Load existing WAI-Point.json if exists."""
        if self.point_file.exists():
            with open(self.point_file, 'r') as f:
                return json.load(f)
        return None
