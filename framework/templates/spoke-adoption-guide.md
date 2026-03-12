# Phase 11: Spoke Adoption Guide - Self-Registry Implementation

**Version:** 1.0
**Date:** 2026-03-12
**Target:** Any spoke adopting Phase 9 architecture
**Expected read time:** 10 minutes

---

## Overview

This guide helps any spoke (email, website, data analysis, etc.) implement the Phase 9 self-declaring architecture. After this guide, your spoke will:

- ✓ Maintain `.spoke-metadata.yaml` declaring what you are and what you do
- ✓ Have metadata automatically aggregated by hub on wakeup
- ✓ Appear in the live registry for accurate help routing
- ✓ Participate in wheel improvement via help feedback loop
- ✓ Track activity metrics (commits, lugs, sessions) for BI

---

## Step 1: Get the Template

Copy `framework/templates/spoke-metadata.yaml.template` to your spoke root:

```bash
cp framework/templates/spoke-metadata.yaml.template .spoke-metadata.yaml
```

---

## Step 2: Populate Identity Section

Fill in who you are:

```yaml
identity:
  path: "project/spoke"                    # e.g., "ezorg/email"
  type: "spoke"                            # spoke | hub | archive
  status: "active"                         # active | archived | suspended
  name: "Human-Readable Name"              # e.g., "Email Management System"
  mission: "One sentence why you exist"    # What is your core purpose?
```

**For Email Spoke:**
```yaml
identity:
  path: "ezorg/email"
  type: "spoke"
  status: "active"
  name: "Email Management System"
  mission: "Manage email organization, inbox processing, and automation workflows for knowledge workers."
```

---

## Step 3: Define Your Scope

What do you do? What are your boundaries?

```yaml
scope:
  domains:
    - "Email workflows and architecture"
    - "Inbox management and automation"
    - "Email-based decision capture"
  boundaries:
    - "We do NOT handle general email protocols (IMAP/SMTP) - that's third-party libraries"
    - "We do NOT implement email encryption (off-the-shelf solutions exist)"
    - "We do NOT manage external email providers (Gmail, Outlook) - we integrate with them"
```

**For Email Spoke:**
```yaml
scope:
  domains:
    - "Email system architecture"
    - "Inbox management patterns"
    - "Email workflow automation"
    - "Message processing and organization"
  boundaries:
    - "We do NOT implement email protocols (SMTP/IMAP) directly"
    - "We do NOT maintain external provider integrations (use their APIs)"
    - "We do NOT handle user authentication (delegate to auth layer)"
```

---

## Step 4: Declare Your Expertise

What can other spokes learn from you?

```yaml
expertise:
  offers:
    - "Email system architecture and patterns"
    - "Inbox automation and workflow design"
    - "Message capture and processing"
    - "Email-based decision workflows"
  stack:
    - "Python 3.8+"
    - "PostgreSQL (message storage)"
    - "Celery (async processing)"
    - "Jinja2 (template workflows)"
  team_model: "Single-agent per session with dogfooding pattern"
```

---

## Step 5: Record Framework State

What framework version are you using? Which skills do you load?

```yaml
framework:
  version: "2.0.0"              # Match framework version you're using
  skills_loaded:
    - "wai (wakeup protocol)"
    - "wai-closeout (session end)"
    - "self-registry (maintain metadata)"
    - "help (navigate registry)"
    - "safe-refactor (structural changes)"
```

---

## Step 6: Populate Activity Metrics

This is the BI section that shows hub your health. **These should be automated by the self-registry skill**, but for now:

```yaml
activity:
  created_at: "2025-12-01T00:00:00Z"     # When was this spoke created?
  last_modified: "2026-03-12T12:00:00Z"  # Now

  git_metrics:
    commits_last_30_days: 15      # git log --since="30 days ago" | wc -l
    last_commit_date: "2026-03-12T12:00:00Z"
    active_branches: 3            # git branch -a | wc -l

  lug_metrics:
    lugs_created_30_days: 3
    open_lugs: 0
    decisions_made: 2

  session_metrics:
    last_session: "2026-03-12T10:00:00Z"
    session_count: 5
    days_since_last_activity: 2

  health_status: "active"  # active | slow | inactive
```

**Interpretation for Hub BI:**
- `commits_last_30_days: 15` → "This spoke is actively developed"
- `health_status: "active"` → "This spoke should be consulted for questions in its domains"
- `days_since_last_activity: 2` → "Recently worked (within 2 days)"

---

## Step 7: Run Validation

Once you've populated the file, validate it:

```bash
python3 << 'EOF'
import yaml
with open('.spoke-metadata.yaml') as f:
    data = yaml.safe_load(f)
    print("✓ Valid YAML")
    print(f"✓ Path: {data['identity']['path']}")
    print(f"✓ Status: {data['identity']['status']}")
    print(f"✓ Domains: {len(data['scope']['domains'])}")
    print(f"✓ Expertise: {len(data['expertise']['offers'])} offerings")
    print(f"✓ Health: {data['activity']['health_status']}")
EOF
```

---

## Step 8: Automate with Self-Registry Skill

**Future:** The `self-registry` skill will automatically:
- Read your EXTENSION.md (identity, mission)
- Count your git commits (activity metrics)
- Scan WAI-Lugs.jsonl (lug metrics, decisions)
- Update `.spoke-metadata.yaml` on demand or periodically
- Create a metadata-updated lug when changed

For now, update manually when:
- You add new expertise/capability
- You change status (active → archived)
- You want to refresh activity metrics

---

## Step 9: Hub Will Read This on Wakeup

When the hub wakes up, it will:

1. **Discover** your spoke (read this file)
2. **Validate** against schema (check all required fields)
3. **Aggregate** into live registry.yaml
4. **Detect changes** (new capabilities, status changes, etc.)
5. **Create administrative lug** logging what changed

---

## Step 10: Agents Will Find You

When an agent asks a question in your domain, the help skill will:

1. Check local files first
2. If not found, check registry
3. See your spoke listed under relevant domains
4. Route question to you
5. You respond or create a lug if question is new

---

## Example: Complete Email Spoke Metadata

```yaml
---
metadata_version: "2.0"
last_updated: "2026-03-12T12:00:00Z"
last_updated_by: "email-spoke"

identity:
  path: "ezorg/email"
  type: "spoke"
  status: "active"
  name: "Email Management System"
  mission: "Manage email organization, inbox processing, and automation workflows. Transform unstructured email into actionable decisions and knowledge."

scope:
  domains:
    - "Email system architecture"
    - "Inbox management and automation"
    - "Email workflow automation"
    - "Message processing and capture"
  boundaries:
    - "We do NOT implement email protocols (SMTP/IMAP) - use third-party libraries"
    - "We do NOT maintain provider integrations (Gmail, Outlook) - integrate with their APIs"
    - "We do NOT handle user auth - delegate to auth system"

expertise:
  offers:
    - "Email system architecture and design patterns"
    - "Inbox automation and workflow design"
    - "Message capture from email and decision extraction"
    - "Email-based automation rules and templates"
  stack:
    - "Python 3.8+"
    - "PostgreSQL"
    - "Celery (async)"
    - "FastAPI (webhooks)"
  team_model: "Single agent per session with email domain expertise"

framework:
  version: "2.0.0"
  skills_loaded:
    - "wai (wakeup)"
    - "wai-closeout (session end)"
    - "self-registry (maintain metadata)"
    - "help (navigate registry)"
    - "safe-refactor (structural changes)"

activity:
  created_at: "2025-12-01T00:00:00Z"
  last_modified: "2026-03-12T12:00:00Z"

  git_metrics:
    commits_last_30_days: 18
    last_commit_date: "2026-03-12T10:30:00Z"
    active_branches: 2

  lug_metrics:
    lugs_created_30_days: 4
    open_lugs: 0
    decisions_made: 3

  session_metrics:
    last_session: "2026-03-12T10:00:00Z"
    session_count: 7
    days_since_last_activity: 2

  health_status: "active"
```

---

## Verification Checklist

- [ ] `.spoke-metadata.yaml` created in spoke root
- [ ] `metadata_version` set to "2.0"
- [ ] `identity.path` matches actual spoke path
- [ ] `identity.mission` is clear (not vague)
- [ ] `scope.domains` are specific (not generic)
- [ ] `scope.boundaries` clearly state what you DON'T do
- [ ] `expertise.offers` match actual capabilities
- [ ] `expertise.stack` lists real technologies
- [ ] `framework.version` matches what you're using
- [ ] `framework.skills_loaded` lists loaded skills
- [ ] `activity` metrics are current (not stale)
- [ ] File validates with YAML parser
- [ ] Committed to git

---

## When to Update

Update `.spoke-metadata.yaml` when:

- ✓ You add new expertise/capability → update `expertise.offers`
- ✓ You change status (active → archived) → update `identity.status`
- ✓ You adopt new major technology → update `expertise.stack`
- ✓ You want to refresh activity metrics → re-count commits, lugs
- ✓ Your mission changes → update `identity.mission`

**Do NOT update:** Last updated timestamp manually (self-registry skill does this).

---

## Next: Hub Registry Aggregation

After all active spokes implement self-registry:

1. Hub runs `registry-refresh` skill on wakeup
2. Hub reads all spokes' `.spoke-metadata.yaml` files
3. Hub aggregates into single `registry.yaml`
4. Registry is always current (never stale)
5. Help skill routes questions accurately

---

## Questions?

If uncertain about any field:
1. Check this guide again
2. Look at framework spoke's `.spoke-metadata.yaml` (example)
3. Create a help-request lug: "How should I fill out .spoke-metadata.yaml?"
4. Framework will improve this guide based on gaps

---

**Spoke Adoption Checklist Version:** 1.0
**Framework Version:** 2.0.0
**Phase:** 11
