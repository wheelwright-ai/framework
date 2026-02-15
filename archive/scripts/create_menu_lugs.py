#!/usr/bin/env python3
"""Create 6 menu improvement lugs"""
from wai.lugs import LugManager
from pathlib import Path

spoke_path = Path('.')
lug_mgr = LugManager(spoke_path)

lugs_to_create = [
    ('Add Branded WAI Intro Banner', 'work', 'medium', 'medium', 
     'Show consistent flashy intro for all WAI invocations - brand recognition + explains what WAI does'),
    ('Remove SCF References from CLI', 'bug', 'medium', 'small',
     'SCF is deprecated - use Wheelwright.AI everywhere'),
    ('Update to WAI Point Reference Only', 'work', 'low', 'small',
     'Instructions should reference WAI Point only for clarity'),
    ('Hide Raw JSON from User Output', 'bug', 'medium', 'small',
     'Raw JSON not helpful in CLI - format or hide it'),
   ('Render Markdown in CLI Output', 'work', 'medium', 'medium',
     'Display markdown formatted not raw text'),
    ('Fix Menu Header Indentation', 'bug', 'low', 'small',
     'Second border should not be indented - alignment issue'),
]

print("Creating lugs...\n")
for title, lug_type, priority, impact, justification in lugs_to_create:
    lug = lug_mgr.create_lug(
        title=title,
        lug_type=lug_type,
        priority=priority,
        impact=impact,
        justification=justification
    )
    print(f"{lug.id} - {title}")

print(f"\n✓ Created {len(lugs_to_create)} lugs")
