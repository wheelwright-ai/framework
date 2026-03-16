# WAI Improve

**Improvement Idea Protocol — capture, evaluate, and prioritize system improvement ideas in the context of this spoke.**

---

## Execution Context

- **Nodes:** spoke, hub
- **Exposure:** spoke.chat:local
- **Trigger:** User submits an idea, agent surfaces a pattern, or `/wai-improve` is called directly

## When to Use

- User has an improvement idea (new or from backlog)
- Agent detects friction, inefficiency, or a recurring pattern worth addressing
- Backlog review — sorting and reframing stale ideas
- After a session reveals a systemic gap worth capturing

---

## Core Principle

**Separate the challenge from the hypothesis.**

The challenge is the *problem worth solving*. The hypothesis is *one possible solution*.
Old ideas almost always have a still-valid challenge — only the hypothesis goes stale.

```
CHALLENGE:  "Agents lose track of which teachings they've already applied"
HYPOTHESIS: "Add a processed/ directory and filename matching"   ← can go stale
             → reframed: "Use lug-based receipt records instead" ← new hypothesis, same challenge
```

Never discard the challenge when the hypothesis is outdated. Reframe.

**You cannot evaluate an idea without understanding the project.** Scoring "velocity lift" for a spoke you haven't loaded is a guess. Recognizing that an idea duplicates existing work is impossible without knowing what exists. Load context and scan the system before evaluating anything.

---

## Execution Flow

```
Step 0: Load spoke context (foundation, boundaries, phase)
   ↓
Step 1: Intake (challenge, hypothesis, origin, scope)
   ↓
Step 2: Similarity and fit check ← must complete before refinement or scoring
   ↓
Step 3: Refinement questions (informed by Steps 0 + 2)
   ↓
Step 3b: Challenge matching (link refined statement → WAI-Challenges.jsonl)
   ↓
Step 4: Evaluation and scoring
   ↓
Step 5: Output as idea lug (or merge/supersede/discard decision)
```

Steps 2 and 3 are the fitting work. They happen in conversation, before any lug is created. A lug that skips these steps is not fully processed and should not be promoted.

---

## Step 0: Load Spoke Context (Required)

Before processing any idea, load and internalize the spoke's context.

### 0a. Read Foundation

From `WAI-Spoke/WAI-State.json`, extract:
- `_project_foundation.identity.one_liner` — what is this project?
- `_project_foundation.identity.success_looks_like` — what does done look like?
- `_project_foundation.boundaries.in_scope` — what is this project committed to?
- `_project_foundation.boundaries.out_of_scope` — what is explicitly excluded?
- `_project_foundation.boundaries.constraints` — what must stay true?
- `_project_foundation.philosophy.core_principle` — what guides decisions?
- `_project_foundation.approach.stack_or_tools` — what is it built with?
- `context.current_phase` — where is the project right now?

Also check `WAI-Spoke/WAI-Lugs.jsonl` for the most recent `ty: "foundation"` lug — it may contain richer or more current context than WAI-State.json.

### 0b. Foundation Completeness Check

| Signal | What It Means |
|--------|--------------|
| `identity.one_liner` is null or generic | Cannot evaluate fit or velocity — ask user to describe the project |
| `boundaries.in_scope` is empty | Cannot evaluate system fit — what counts as aligned? |
| `boundaries.constraints` is empty | Cannot evaluate cost or risk |
| `context.current_phase` is null | Cannot weight urgency |
| No foundation lug exists at all | **Stop. Run `/wai-foundation` before evaluating any ideas.** |

If critical fields are missing:
> "Before I can evaluate this well, I need to understand [X]. Can you fill me in, or should we run `/wai-foundation` first?"

Do not invent context. Do not assume. Ask.

### 0c. Build Scoring Context

With foundation loaded, translate the four scoring dimensions into spoke-specific terms. Write a one-line definition of each before evaluating any idea:

- **Velocity lift for this project:** What does "faster" mean here? (derive from `success_looks_like` + `current_phase`)
- **System fit for this project:** What is aligned vs out of scope? (derive from `in_scope`, `out_of_scope`, `philosophy`)
- **Implementation cost for this project:** What makes something cheap or expensive here? (derive from `stack_or_tools`, `constraints`)
- **Generality for this project:** Who does this affect — just this spoke, or the wider network?

Show these to the user at the start of a backlog session so the scoring rubric is shared and agreed.

---

## Step 1: Intake

When receiving an idea, extract or prompt for four things:

**Challenge** — the stable part. What breaks, slows, or is missing?
- If vague: "What breaks or feels wrong without this?"
- Must be present before proceeding

**Hypothesis** — the testable part. What change would address it?
- Format: "If we [do X], then [outcome Y] because [reason Z]"
- A hypothesis without a mechanism is still vague — push for the mechanism

**Origin** — `user` / `agent` / `signal` / `backlog`

**Scope** — `skill` / `protocol` / `schema` / `tooling` / `multi` / `trivial`

**Trivial path:** If scope is `trivial` (single-line edits, typo fixes, config value changes, obvious non-overlapping additions) skip Steps 2–4 entirely. Go directly to Step 5 with a minimal lug: challenge and hypothesis collapsed into `t`, no scoring, `priority: P0`, `fit_classification: net_new` assumed. Use sparingly — if there is any doubt about overlap or fit, use a real scope and run the full protocol.

---

## Step 2: Similarity and Fit Check

**This step is mandatory before refinement questions and before any lug is created.**

The purpose is not just deduplication — it is *fitting*. An idea doesn't exist in isolation. It lands somewhere in the current system. This step finds where it lands, whether the terminology matches, and whether the right framing has been used. The outcome shapes what refinement questions you ask.

### 2a. Scan Open Lugs

Read `WAI-Spoke/WAI-Lugs.jsonl`. De-duplicate by ID (latest entry wins). Filter to active lugs: `s` in `o` (open), `p` (in-progress). Skip closed/resolved.

For each active lug, assess similarity to the incoming idea's **challenge** and **hypothesis**:

| Similarity Type | Definition | Action |
|----------------|------------|--------|
| **Exact** | Same challenge and same mechanism | Flag as duplicate — present existing lug, ask user to confirm merge or distinguish |
| **Challenge overlap** | Same problem, different proposed solution | Flag as related — the ideas may be competing hypotheses for the same challenge |
| **Hypothesis overlap** | Different problem framing, same proposed mechanism | Flag — may indicate a terminology mismatch or a broader opportunity |
| **Dependency** | The incoming idea requires this lug to be resolved first | Note as blocker |
| **Conflict** | The incoming idea contradicts or replaces what this lug is tracking | Flag — needs explicit decision before proceeding |

Present any matches. Do not suppress findings. One sentence per match is enough:
> "Open lug `epic-X` tracks [challenge] via [mechanism] — your idea overlaps on [what]."

### 2b. Scan Existing Skills and Functionality

Check `templates/commands/` (or `WAI-Spoke/commands/` if local overrides exist) for skills that already address any part of the challenge.

Also check:
- `WAI-Spoke/skills/` — local skill files
- `WAI-Spoke/WAI-State.json` → `features[]` — declared existing features
- `WAI-Spoke/_project_foundation` → `in_scope[]` — committed work that may already be underway

For each relevant file or feature, assess:
- **Full coverage** — the system already does what the hypothesis describes
- **Partial coverage** — the system does part of it; the idea extends or fills a gap
- **Terminology gap** — the system has this concept under a different name

### 2c. Scan Signals and Decisions

Read `WAI-Spoke/WAI-Signals.jsonl`. For signals with impact >= 7, check whether any captured decision:
- Already resolved the challenge (idea may be stale)
- Ruled out the proposed mechanism ("we decided not to do X because Y")
- Established a precedent that the idea should follow

### 2d. Terminology Reconciliation

The most common fitting problem is terminology drift — the user uses one word, the system uses another for the same concept. Surface mismatches explicitly:

| User's term | System's existing term | Relationship |
|-------------|----------------------|--------------|
| "inbox processing" | `wai-learn` / inbox protocol | Same concept |
| "idea queue" | `ty: "idea"` lugs | Same concept |
| "project memory" | foundation lug + WAI-State.json | Partial — foundation is the structured part |
| "send to another project" | `/wai-teach` outbox delivery | Same concept |

If terminology mismatches are found, name them before proceeding:
> "You called this [user term] — the system already uses [system term] for this. Are you extending that, or describing something different?"

This is not pedantry. A wrongly-named idea creates a wrongly-named lug that misleads the next session.

### 2e. Produce Fit Report

After scanning, present a fit report before asking refinement questions:

```
### Fit Report — {idea title}

**Existing lug overlap:**
- {lug id} "{title}": {similarity type} — {one sentence on what overlaps}
  (none found)

**Existing functionality overlap:**
- {skill/feature}: {full/partial coverage} — {what it already handles}
  (none found)

**Signal/decision conflicts:**
- {signal summary}: {how it relates}
  (none found)

**Terminology notes:**
- "{user term}" → system calls this "{system term}"
  (none found)

**Fit classification:** net_new | extends | supersedes | conflicts | duplicate
```

**Fit classifications:**
- `net_new` — no meaningful overlap; proceed as a new idea
- `extends` — builds on existing lug or skill; reference it in the new lug's `related_lugs`
- `supersedes` — replaces existing lug or skill; old lug should be reconciled when this is implemented
- `conflicts` — contradicts an open lug or prior decision; must resolve conflict before proceeding
- `duplicate` — already tracked; redirect user to the existing lug instead of creating a new one

If `duplicate` or `conflicts`: **stop here**. Do not proceed to refinement or scoring until the user acknowledges the finding and decides how to proceed.

---

## Step 3: Refinement Questions

After intake and fit check, ask refinement questions **grounded in both spoke context (Step 0) and fit findings (Step 2)**. This is where fitting is completed before the idea is locked in.

### How to Generate Questions

If the fit check found overlaps, the first questions address those:
- "How is this different from `{overlapping lug}`?"
- "Does this replace `{skill}` entirely, or work alongside it?"
- "You used the term `{user term}` — does that map to what the system calls `{system term}`, or is it something new?"

Then look for tensions with the foundation:
- Stated constraints (does this idea introduce a dependency the project excluded?)
- Current phase (is this the right time, or does it conflict with in-flight work?)
- Philosophy (does the mechanism align with how this project makes decisions?)
- Stack/tools (is this buildable with what's here?)

### Standard Fallback Questions

If foundation is thin or fit check found nothing:
1. Is the challenge currently blocking anything active?
2. What would be measurably different after this is implemented?
3. Does this need to work across spokes, or just here?

Ask at most 3 questions at a time. Wait for answers. The answers may change the fit classification.

---

## Step 3b: Challenge Matching

After Step 3, the challenge statement is in its canonical (refined) form. Match it against `WAI-Spoke/WAI-Challenges.jsonl` to link this idea to an existing problem or create a new one.

If `WAI-Spoke/WAI-Challenges.jsonl` does not exist, create it as an empty file before proceeding.

### Normalization pipeline

Apply this pipeline to the challenge statement before comparison:

1. Lowercase
2. Strip punctuation
3. Tokenize on whitespace
4. Remove stopwords (same list as `historian.yaml` → `pattern_scan.algorithm`)
5. Apply Porter stemming (`detect`, `detecting`, `detection` → `detect`)

### Matching

Compute Jaccard similarity between normalized tokens of the intake challenge and each existing challenge entry:

```
similarity = |tokens(A) ∩ tokens(B)| / |tokens(A) ∪ tokens(B)|
```

Threshold: **0.5**

### If match found (similarity >= 0.5)

Present to user:
> This challenge overlaps with existing challenge `{i}`: "{statement}" (similarity: {score}). Same problem? [enter=yes / type correction]

On confirmation: set `challenge_id` = existing challenge `i`. Append an override entry to `WAI-Challenges.jsonl` adding the new idea ID to `related_lugs` (same `i`, updated fields — latest entry per `i` wins, same convention as `WAI-Lugs.jsonl`).

### If no match

Propose a new challenge entry:
> No existing challenge found. Proposed:
> `chal-{3-5-word-slug}`
> statement: "{refined challenge text}"
> [enter=accept / edit]

On accept (or no response): append new entry to `WAI-Challenges.jsonl`:

```json
{
  "i": "chal-{slug}",
  "ty": "challenge",
  "statement": "{refined challenge text}",
  "first_seen": "ISO-8601",
  "first_seen_in": "{idea lug id — update at Step 5 after lug is written}",
  "status": "open",
  "related_lugs": [],
  "resolution_notes": null
}
```

Set `challenge_id` to this new `i`.

**Sequencing note:** `first_seen_in` references the idea lug ID that will be written at Step 5. After writing the idea lug, append one more override entry to `WAI-Challenges.jsonl` to set `first_seen_in` and add the idea ID to `related_lugs`.

### Slug generation

Take 3–5 most meaningful words from the challenge statement (nouns and verbs — skip stopwords and filler). Join with hyphens, lowercase.

Example: `"Recurring friction across sessions is invisible"` → `chal-recurring-friction-invisible`

---

## Step 4: Evaluation and Scoring

After Steps 0–3, score on four dimensions using the spoke-specific translations from Step 0c.

Each dimension: **low / medium / high**.

### 1. Velocity Lift
*How much does this speed up the human-AI collaboration cycle for this project?*
Calibrated against the spoke-specific definition. Flag uncertainty explicitly.

### 2. Implementation Cost
*How much work is this, given stack and constraints?*
- **Low** — additive single-file change, no migration (1 session)
- **Medium** — new skill + type + tests, or cross-file protocol change (2–3 sessions)
- **High** — architectural change, migration required, or multiple spokes affected (epic-level)

Adjust for existing state. A "low" in isolation may be "medium" if the project has fragile existing data.

### 3. System Fit
*Does this align with this project's philosophy, boundaries, and existing patterns?*
Use the spoke-specific definition. If fit check flagged `tension`, this dimension should reflect that.

- **Aligned** — extends existing patterns naturally
- **Neutral** — independent of core patterns
- **Tension** — introduces complexity or conflicts with stated boundaries

### 4. Generality
*Who benefits?*
- **All spokes** — improves every project using Wheelwright
- **Hub** — improves cross-spoke coordination
- **Framework** — improves the authoring/distribution workflow
- **Single spoke** — local improvement only

---

## Priority Classification

Base priority from velocity + cost + fit:

| Velocity | Cost | Fit | → Base Priority |
|----------|------|-----|-----------------|
| High | Low | Aligned | **P0 — Do next** |
| High | Low | Neutral/Tension | **P1 — Do soon, watch fit** |
| High | Medium | Aligned | **P1 — Plan carefully** |
| High | High | Aligned | **P2 — Epic needed** |
| Medium | Low | Aligned | **P2 — Quick win** |
| Medium | Medium | Any | **P3 — Backlog** |
| Low | Any | Any | **P4 — Defer** |
| Any | Any | Tension | **⚠ flag: revisit design before starting** |

### Phase Adjustment

After deriving base priority, adjust one tier based on `context.current_phase` loaded in Step 0. The same idea has different urgency depending on where the project is.

| Phase | Emphasizes | Adjustment |
|-------|-----------|------------|
| `early-build` / `active-development` | Velocity — ship fast, learn fast | +1 tier if `velocity: high`. No change otherwise. |
| `stabilization` / `hardening` | Fit — don't introduce new instability | −1 tier if `system_fit: neutral` or `tension`. |
| `scale-out` / `distribution` | Generality — does it help other spokes too? | +1 tier if `generality: all-spokes` or `hub`. |
| `maintenance` | Cost — avoid unnecessary churn | −1 tier if `implementation_cost: high`. |
| `unknown` / null | No adjustment. | Use base priority as-is. |

Tier adjustment: P0→P0 (can't go higher), P4→P4 (can't go lower). One adjustment only — do not stack multiple phase rules.

Show final priority as: `P{N} (base P{N}, adjusted for {phase})` so the reasoning is visible.

### Override Rules

- `scope: schema` or `scope: protocol` → require design discussion before starting (no quick-wins)
- `generality: all-spokes` + `P0/P1` → candidate for teaching file distribution
- `system_fit: tension` → no start without explicit design discussion
- `fit_classification: conflicts` → no start until conflict is resolved
- Foundation incomplete → no idea promoted above P3 until foundation is established

---

## Step 5: Output as Idea Lug

Every fully-processed idea becomes a lug in `WAI-Lugs.jsonl`. "Fully processed" means Steps 0–4 complete.

```json
{
  "i": "idea-{slug}-v{N}",
  "ty": "idea",
  "t": "Short title — in system terminology after reconciliation",
  "s": "proposed",
  "ca": "ISO-8601",
  "gb": "user | agent",
  "challenge": "What problem this solves — the stable part",
  "hypothesis": "Proposed mechanism — the testable part",
  "prior_hypothesis": "Original hypothesis if reframed (omit if not reframed)",
  "reframe_notes": "Why hypothesis changed (omit if not reframed)",
  "origin": "user | agent | signal | backlog",
  "challenge_id": "chal-{slug} — ID from WAI-Challenges.jsonl. Set in Step 3b. Required on fully-processed ideas.",
  "scope": "skill | protocol | schema | tooling | multi",
  "spoke_context_loaded": true,
  "fit_classification": "net_new | extends | supersedes | conflicts | duplicate",
  "related_lugs": ["lug-ids found in fit check"],
  "terminology_reconciled": ["user term → system term if any mismatches resolved"],
  "scores": {
    "velocity_lift": "high | medium | low",
    "implementation_cost": "low | medium | high",
    "system_fit": "aligned | neutral | tension",
    "generality": "all-spokes | hub | framework | single-spoke"
  },
  "priority": "P0 | P1 | P2 | P3 | P4",
  "next_step": "discuss | prototype | epic | defer | discard",
  "agent_framing": "Agent's sharpened statement after discussion (if improved)",
  "_behavior_directive": {
    "what_this_is": "A structured improvement idea. Evaluate before acting.",
    "what_this_is_NOT": "An instruction to implement. Requires explicit user direction."
  }
}
```

**Required fields that prove the idea was fully processed:**
- `spoke_context_loaded: true` — Step 0 completed
- `fit_classification` — Step 2 completed
- `challenge` and `hypothesis` — Step 1 completed
- `challenge_id` — Step 3b completed
- `priority` — Step 4 completed

A lug missing any of these was not fully processed. Treat it as `s: raw` regardless of what it says.

### Status Lifecycle

```
raw → evaluating → proposed → approved → (epic created)
                ↓                      ↘ deferred
             reframed                  ↘ discarded
                ↓                      ↘ merged (into existing lug)
             proposed                  ↘ supersedes (old lug reconciled on implementation)
```

---

## Step 6: Promotion Protocol — Proposed → Approved (Ready to Build)

An idea lug at `s: proposed` is well-understood but not yet actionable. This step is the gate from *understood idea* to *buildable lug*. It must complete before any epic or task lug is created from the idea.

Do not run this step speculatively. Run it when the user says "let's move this forward" or when the idea reaches P0/P1 priority and the user wants to act on it.

### 6a. Draft PEV Fields

A build-ready lug needs three fields that an idea lug does not have:

**Perceive** — What does an agent look at first, before taking any action?
- Specific files, not "relevant files"
- Specific fields within those files, not "check the state"
- Specific conditions to confirm (e.g. "confirm `wai-improve.md` does not already contain `fit_classification`")
- If the agent can't find the starting point from this field alone, it's not specific enough

**Execute** — Numbered, concrete steps.
- Each step is one action, not a cluster of actions
- File paths are absolute or relative to a named root — no ambiguity
- Order matters — sequence explicitly
- Steps that depend on previous steps say so ("after step 3 confirms X, do Y")
- No vague verbs: not "update", "handle", "manage" — use "append", "replace lines N–M with", "create file at path with content"

**Verify** — How does an agent know it is done?
- Each verify item is a checkable condition, not a feeling
- Prefer: "grep confirms X in file Y", "git status shows clean", "function returns Z"
- Avoid: "works correctly", "looks right", "seems complete"

Draft these three fields in conversation with the user. Do not invent specifics the user hasn't confirmed.

### 6b. Unresolved Question Check

Before promotion, confirm nothing from prior steps is still open:
- Fit check: no `conflicts` classification that wasn't resolved
- Refinement questions: all asked questions were answered
- Terminology: all mismatches reconciled — idea lug title and fields use system terms
- Hypothesis: mechanism is specific, not "some kind of X"

If any are open, surface them now. Do not promote with open questions — they become invisible gaps in the next session.

### 6c. Dogfood Check

The most important gate. Read the drafted PEV fields as a naive agent would — no chat history, no prior sessions, only the lug.

Run three audits:

**Perceive audit**
- Does each item name a specific file or directory? (not "relevant files")
- Does each item name a specific field, line, or condition? (not "check the state")
- Could an agent locate the starting point cold, with no prior context?
→ **Pass:** all items are unambiguously locatable.
→ **Fail:** any item requires guessing or inference. Rewrite that item.

**Execute audit**
- Are steps numbered and ordered?
- Does each step contain exactly one action? (not "update and verify" in one step)
- Are all file paths explicit — absolute or relative to a named root?
- Are vague verbs absent? ("update" → "replace line N with X", "handle" → specific action)
- Does each step that depends on a prior step say so explicitly?
→ **Pass:** an agent can execute step N knowing only steps 1..N-1 and the lug.
→ **Fail:** any step requires guessing a value, path, or action. Rewrite that step.

**Verify audit**
- Is each item a checkable condition, not a feeling?
- Does each item specify what to check and what the expected result is?
- Are "works correctly", "looks right", "seems complete" absent?
→ **Pass:** all items can be confirmed true/false with no prior context.
→ **Fail:** any item requires judgment or context not in the lug. Replace it.

**Outcome:** All three pass → proceed to 6d. Any fail → fix and re-audit that section only.

### 6d. Complexity Check

Before marking approved, assess whether the implementation triggers the complexity advisor:
- Does it touch 2 or more files? → planning gate applies
- Does it require 6 or more steps? → planning gate applies

If yes: note in the idea lug that `/wai-complexity-advisor` should be run at implementation start. Do not run the complexity advisor now — that happens in the implementation session, not the idea session.

### 6e. User Approval

After 6a–6d are complete, present the final lug fields to the user:

```
### Ready for approval — idea-{slug}-v{N}

**Challenge:** {challenge}
**Hypothesis:** {hypothesis}
**Perceive:** {perceive}
**Execute:**
  1. {step}
  2. {step}
  ...
**Verify:** {verify items}

**Priority:** P{N}
**Scope:** {scope}
**Fit:** {fit_classification}
**Related:** {related_lugs or none}

Approve? (yes to promote / adjust to revise / defer to backlog)
```

On approval:
- Update `s` from `proposed` to `approved` in the idea lug
- Add PEV fields to the lug
- The lug is now ready to be promoted to an epic or task in a future session

### 6f. What Comes Next

A `s: approved` idea lug is the input to an implementation session, not the implementation itself. In the next session:
1. Read the idea lug
2. Run `/wai-complexity-advisor` if triggered
3. Create an epic or task lug from it (the idea lug's PEV fields become the epic's PEV fields)
4. Close the idea lug (`s: c`, `superseded_by: epic-id`)

The idea lug is not discarded — it is the record of why the epic exists.

---

## Backlog Review Mode

When reviewing a backlog of existing ideas:

1. Load spoke context (Step 0)
2. Read all `ty: "idea"` lugs — de-duplicate by ID
3. For each idea: re-run Step 2 (fit check) against current state — the system has changed since the idea was logged
4. Group findings:

```
### Idea Backlog — {project name}

Context loaded: {one_liner}
Current phase: {phase}

**Ready to promote (challenge valid, fit clean, hypothesis current):**
- idea-X: {title} — P{N}

**Needs reframe (challenge valid, hypothesis stale):**
- idea-Y: {title} — {what changed}

**Merge candidates (overlapping challenges):**
- idea-A + idea-B — {shared challenge}

**Now duplicate (system already does this):**
- idea-Z: {title} — covered by {skill/lug}

**Recommend discard (challenge no longer relevant):**
- idea-W: {title} — {why}
```

Present the grouped summary. Let the user choose which group to tackle first. Do not process the entire backlog sequentially without user direction.

---

## Reframe Protocol

For any idea where the hypothesis is stale but the challenge is still valid:

1. Preserve challenge verbatim in `challenge`
2. Move old hypothesis to `prior_hypothesis`
3. Write new hypothesis based on current system state
4. Add `reframe_notes` — one sentence on what changed that made the old hypothesis stale
5. Re-run Step 2 with the new hypothesis — the fit classification may change

---

## Agent-Initiated Ideas

Agents surface ideas when they observe:
- Repeated manual steps that could be captured in protocol
- A workaround used more than once
- A gap between what a skill says and what actually works
- A pattern across multiple session tracks

Agent surfaces an idea as:
> "I noticed [observation]. Challenge: [challenge]. Hypothesis: [hypothesis]. Worth running through /wai-improve?"

Agent does NOT create the lug without user acknowledgment. User steers whether to process, discuss, or drop.

---

## Distribution Note

This skill is distributed to all spokes via `/wai-teach`. When it runs on a spoke, it reads **that spoke's** foundation, open lugs, skills, and signals. It does not carry framework-specific assumptions. The fit check in Step 2 runs against the receiving spoke's own state.

Quality of output scales with quality of foundation. A spoke with a thin foundation and stale lugs will produce less useful fit reports. The skill surfaces this rather than hiding it.

---

## Related Skills

- `/wai-foundation` — required before evaluating ideas on an unfamiliar project
- `/wai-lug-advisor` — lug schema and authoring rules
- `/wai-complexity-advisor` — planning gate before implementation begins
- `/wai-stewardship-advisor` — scope drift detection during implementation

---

*Fitting is the work. An idea that hasn't been fit into the current system is just a wish.*
