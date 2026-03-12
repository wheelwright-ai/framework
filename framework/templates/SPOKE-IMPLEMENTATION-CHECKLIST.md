# Phase 12: Spoke Implementation Checklist

**Version:** 1.0
**Date:** 2026-03-12
**Status:** Active Implementation Phase
**Target Spokes:** Email (ezorg/email), Website (wheelwright/website)

---

## Implementation Steps for Each Spoke

### For Email Spoke (ezorg/email)

**Location:** Spoke's root directory (where .git exists)
**File to create:** `.spoke-metadata.yaml`

**Step 1: Copy Template**
```bash
cd /path/to/ezorg-email-website  # or ezorg/email repo
cp /path/to/wheelwright/framework/templates/spoke-metadata.yaml.template .spoke-metadata.yaml
```

**Step 2: Fill In (Use Email Example as Reference)**
- Reference: `framework/templates/spoke-metadata.ezorg-email.example.yaml`
- Key sections:
  - `identity.path`: "ezorg/email"
  - `identity.mission`: "Manage email organization, inbox processing, and automation workflows..."
  - `scope.domains`: email architecture, inbox automation, workflow, message capture
  - `expertise.offers`: 4 offerings (email architecture, inbox automation, message capture, automation rules)
  - `expertise.stack`: Python, PostgreSQL, Celery, FastAPI
  - `framework.version`: "2.0.0"
  - `activity`: Real git metrics, lug counts, session data

**Step 3: Validate**
```bash
python3 << 'EOF'
import yaml
with open('.spoke-metadata.yaml') as f:
    data = yaml.safe_load(f)
    assert data['identity']['path'] == 'ezorg/email'
    assert data['identity']['status'] == 'active'
    assert len(data['scope']['domains']) > 0
    assert len(data['expertise']['offers']) > 0
    print("✓ Email spoke metadata valid")
EOF
```

**Step 4: Commit**
```bash
git add .spoke-metadata.yaml
git commit -m "feat: Self-registry metadata for email spoke (Phase 12)

Implements Phase 9 self-declaring architecture.
Hub will read this metadata on wakeup and aggregate into registry.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

**Step 5: Wait for Hub**
- Hub's next wakeup will read `.spoke-metadata.yaml`
- Hub will aggregate into `hub/registry.yaml`
- Hub will create administrative lug documenting the metadata aggregation
- Registry will be updated with email spoke's latest capabilities

---

### For Website Spoke (wheelwright/website)

**Location:** Spoke's root directory
**File to create:** `.spoke-metadata.yaml`

**Step 1: Copy Template**
```bash
cd /path/to/wheelwright-ai-website  # or wheelwright/website repo
cp /path/to/wheelwright/framework/templates/spoke-metadata.yaml.template .spoke-metadata.yaml
```

**Step 2: Fill In (Use Website Example as Reference)**
- Reference: `framework/templates/spoke-metadata.wheelwright-website.example.yaml`
- Key sections:
  - `identity.path`: "wheelwright/website"
  - `identity.mission`: "Create user-facing documentation and marketing website..."
  - `scope.domains`: user documentation, marketing messaging, onboarding, API documentation
  - `expertise.offers`: 4 offerings (doc generation, marketing strategy, onboarding, API docs)
  - `expertise.stack`: Next.js, TypeScript, Markdown, Docusaurus, Netlify
  - `framework.version`: "2.0.0"
  - `activity`: Real git metrics, lug counts, session data

**Step 3: Validate**
```bash
python3 << 'EOF'
import yaml
with open('.spoke-metadata.yaml') as f:
    data = yaml.safe_load(f)
    assert data['identity']['path'] == 'wheelwright/website'
    assert data['identity']['status'] == 'active'
    assert len(data['scope']['domains']) > 0
    assert len(data['expertise']['offers']) > 0
    print("✓ Website spoke metadata valid")
EOF
```

**Step 4: Commit**
```bash
git add .spoke-metadata.yaml
git commit -m "feat: Self-registry metadata for website spoke (Phase 12)

Implements Phase 9 self-declaring architecture.
Hub will read this metadata on wakeup and aggregate into registry.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

**Step 5: Wait for Hub**
- Hub's next wakeup will read `.spoke-metadata.yaml`
- Hub will aggregate into `hub/registry.yaml`
- Hub will create administrative lug documenting the metadata aggregation
- Registry will be updated with website spoke's latest capabilities

---

## Hub Registry Aggregation (After Spoke Implementation)

When hub wakes up after spokes implement metadata:

```
Step 1: Discover active spokes
  - Read from hub/registry.yaml (existing nodes)
  - Read from git (spoke directories)
  - Check for new spoke announcements

Step 2: Collect spoke metadata
  - Read wheelwright/framework/.spoke-metadata.yaml ✓ (already done)
  - Read ezorg/email/.spoke-metadata.yaml (when email spoke implements)
  - Read wheelwright/website/.spoke-metadata.yaml (when website spoke implements)

Step 3: Validate against schema
  - All required fields present ✓
  - Activity metrics current ✓
  - Status values valid ✓

Step 4: Detect changes
  - Framework: expertise 4→7 (already detected in Phase 10)
  - Email: first implementation (new to registry)
  - Website: first implementation (new to registry)

Step 5: Aggregate into live registry.yaml
  - Add framework spoke with 7 expertise offerings
  - Add email spoke with 4 expertise offerings
  - Add website spoke with 4 expertise offerings
  - Update counts: active nodes, total expertise areas, BI metrics

Step 6: Log changes
  - Create administrative lug: "Hub registry aggregated from 3 spoke metadata files"
  - Record which spokes were new vs. updated
  - Record changes in expertise (4→7 for framework)
  - Timestamp: when aggregation occurred
```

---

## Testing After Implementation

### Test 1: Hub Registry Aggregation
```bash
# After spokes implement and hub wakes up:
grep -A 30 'path: "ezorg/email"' hub/registry.yaml
# Should show email spoke with expertise from .spoke-metadata.yaml

grep -A 30 'path: "wheelwright/website"' hub/registry.yaml
# Should show website spoke with expertise from .spoke-metadata.yaml
```

### Test 2: Help Skill Routing
```
Agent asks: "How do I set up email automation?"
Expected: Route to ezorg/email (registered in metadata)

Agent asks: "How should we document this feature?"
Expected: Route to wheelwright/website (registered in metadata)

Agent asks: "How does WAI handle lugs?"
Expected: Route to wheelwright/framework (WAI mechanics authority)
```

### Test 3: Activity Metrics Visibility
```bash
# Check that hub sees activity metrics
jq '.nodes[] | select(.path == "ezorg/email") | .activity_metrics' hub/registry.yaml
# Should show: commits_30d, lugs_created_30d, last_session, health_status

jq '.nodes[] | select(.path == "wheelwright/website") | .activity_metrics' hub/registry.yaml
# Should show real activity data from website spoke
```

---

## Phase 12 Success Criteria

- [ ] Email spoke implements `.spoke-metadata.yaml` (guides followed, file created, committed)
- [ ] Website spoke implements `.spoke-metadata.yaml` (guides followed, file created, committed)
- [ ] Both files validate against schema
- [ ] Framework spoke metadata verified from Phase 9 ✓ (already done)
- [ ] Hub successfully reads all 3 spoke metadata files (test after spokes implement)
- [ ] Registry aggregates correctly with all spokes (test after spokes implement)
- [ ] Help skill routes to correct spokes using aggregated registry (test after spokes implement)
- [ ] Activity metrics flow correctly (commits, lugs, sessions visible in registry)
- [ ] No conflicts or schema violations
- [ ] All changes documented in lugs

---

## Known Spoke Paths (From Current Registry)

**Active Spokes:**
- `wheelwright/framework` — Framework spoke ✓ (Phase 9-10 complete)
- `wheelwright/hub` — Hub spoke (maintains registry, patterns)
- `wheelwright/website` — Website spoke (TARGET for Phase 12)
- `ezorg/email` — Email spoke (TARGET for Phase 12)

**Archived Spokes:** (14 historical projects)
- `archive/OwnersShare-pitch`, `archive/VoiceFlow`, `archive/CondoShield-*`, etc.

---

## Timeline

**Phase 9:** Framework spoke self-registry validation ✓ (2026-03-12)
**Phase 10:** Hub registry-refresh & help routing validation ✓ (2026-03-12)
**Phase 11:** Spoke adoption guide & examples created ✓ (2026-03-12)
**Phase 12:** Email & website spokes implement metadata (IN PROGRESS)
**Phase 13:** Real hub aggregation test (after spokes implement)
**Phase 14:** Live help routing with real spokes (after hub aggregation works)
**Phase 15:** Ongoing wheel improvement via feedback loop

---

## Support & Questions

If a spoke needs help implementing:

1. Reference `framework/templates/spoke-adoption-guide.md` (10 steps)
2. Look at `framework/templates/spoke-metadata.{example-spoke}.yaml`
3. Use `framework/templates/spoke-metadata.yaml.template` as base
4. Create help-request lug if unclear: "How should I fill out .spoke-metadata.yaml?"
5. Framework will improve guide based on feedback

---

**Phase 12 Checklist Version:** 1.0
**Framework Version:** 2.0.0
**Ready for:** Email and website spokes to implement
