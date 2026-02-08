# WAI Teach

Pull new learnings from hub into this spoke.

## Instructions

1. Check hub location from WAI-Spoke/WAI-State.json -> wheelwright.hub_path

2. If hub path exists, check for new knowledge:
   - Read hub knowledge base version
   - Compare with spoke kb-sync.json
   - Check for updated skill files in hub templates/commands/

3. If new learnings available:
   - List what is new (patterns, policies, skills, etc.)
   - Ask user to confirm import
   - If skill files updated: Copy new/updated .md files from hub templates/commands/ to spoke templates/commands/
   - Update WAI-Guide.md with new Hub Learnings section
   - Update kb-sync.json with new version

4. Skill File Sync:
   - Hub maintains authoritative skill definitions in templates/commands/
   - On teach, spoke receives latest 16 skill .md files
   - Skills always in sync across framework and all spokes

5. If WAI CLI available, suggest: WAI sync --teach

Output format:
Hub Teachings Available

New since last sync:
- [Pattern/Learning 1]
- [Pattern/Learning 2]
- [Skill Updates: X skills updated]

Import these learnings? (yes/no)

Or if nothing new:
Hub Sync Current
No new teachings since last sync ([date]).
Skills already at latest version.
