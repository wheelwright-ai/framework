# Reference Documentation

This directory contains historical and architectural documentation from WAI framework development.

## Structure

### `/historical/` (111 files)
Session notes, implementation logs, closeouts, and phase completion docs from WAI development. These documents capture the journey of building WAI v1 through v2.

**Categories:**
- `CLI-*.md` - CLI development and usability iterations
- `CLOSEOUT-*.md` - Session closeout notes
- `SESSION-*.md` - Session summaries and deliverables
- `PHASE*.md` - Phase completion reports
- `IMPLEMENTATION-*.md` - Implementation notes
- `DELIVERY-*.md` - Delivery checklists and reports
- `OBSERVATION-*.md` - Observation system development
- `TEACH-*.md` - Teaching/learning system development
- `MACHINE-*.md` - Machine-aware optimization development

**Value:** These docs show how decisions were made, what was tried, and why things evolved. Useful for understanding design rationale.

### `/architecture/` (8 files)
Architectural documentation and design decisions.

**Contents:**
- `AGENTS.md` - Agent identity and behavior
- `AGENTS-MD-*.md` - Agents.md specification evolution
- `ARCHITECTURE-*.md` - Hub-spoke architecture design
- `HUB-*.md` - Hub implementation status
- `LUG-SYSTEM-*.md` - Lug system specification

**Value:** Core architectural decisions that shaped WAI. Reference when making structural changes.

## Usage

These files are **read-only reference material**, not active documentation.

For current documentation, see:
- `/framework/docs/` - Active user-facing documentation
- `WAI-Lug-Schema-Spec.md` - Current Lug specification (root)
- `WAI-Skill-Contract-Spec.md` - Current Skill specification (root)
- `hub/BRIEF.md` - Current policies and communication style

## Historical Context

WAI evolved through several major phases:
1. **SCF (Session Continuity Framework)** - Original concept
2. **Wheelwright v1** - CLI-based approach (abandoned after Hub destruction incident)
3. **Wheelwright v2** - File-based protocol with Skills and Lugs (current)

These reference docs capture that evolution.
