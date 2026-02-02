# Hub Persona A/B Testing System

**Self-Optimizing AI Collaboration Through Continuous Experimentation**

## Vision

Hub learns optimal persona/tone for working with you across different projects and LLM models by:
1. Maintaining centralized persona preferences as lugs
2. A/B testing variations across spokes
3. Collecting engagement metrics
4. Promoting winning variants
5. Distributing customized directives via teach mechanism

**Key Insight:** Your AI partners should continuously improve how they work with you, learning from every interaction.

## Architecture

### Hub: Centralized Learning

Hub maintains persona knowledge base:
```
hub/
├── WAI-Spoke/
│   ├── WAI-Lugs.jsonl (persona lugs)
│   └── WAI-State.json (A/B test state)
├── learnings/
│   └── persona.jsonl (engagement metrics)
└── experiments/
    └── active-tests.json (running A/B tests)
```

### Spoke: Customized Application

Each spoke receives persona directives:
```
project/
├── WAI-Spoke/
│   ├── WAI-Point.json (persona context from hub)
│   └── seed/ingest/
│       └── persona-directive.teaching
└── AGENTS.md (applied persona instructions)
```

## Data Model

### Persona Lug Structure

**Hub: `hub/WAI-Spoke/WAI-Lugs.jsonl`**

```jsonl
{"i": "persona_001", "t": "Communication Style: Direct & Technical", "ty": "persona", "s": "open", "p": "high", "im": "high", "v": 9, "pt": ["persona", "communication"], "j": "User prefers minimal fluff, max substance", "ex": {"directive": "Skip pleasantries. Dive into technical details immediately.", "tone": "professional-casual", "code_examples": "always-show-code", "engagement_score": 8.7, "sample_size": 47, "variant_id": "v2", "promoted_from": "v1", "promoted_at": "2026-01-15T10:30:00Z"}}
{"i": "persona_002", "t": "Code Style: Pythonic Readability", "ty": "persona", "s": "open", "p": "high", "im": "medium", "v": 8, "pt": ["persona", "code-style"], "j": "User values readable over clever code", "ex": {"directive": "Prefer explicit over implicit. Avoid one-liners if they reduce clarity.", "engagement_score": 8.2, "sample_size": 52, "variant_id": "v1"}}
{"i": "persona_003", "t": "Response Length: Concise", "ty": "persona", "s": "testing", "p": "medium", "im": "medium", "v": 7, "pt": ["persona", "response-format", "ab-test"], "j": "Testing if shorter responses improve velocity", "ex": {"directive": "Target 1-3 sentences for simple answers. Expand only when complex.", "variant_id": "v3_short", "test_id": "test_resp_length_001", "control_variant": "v2_medium", "started_at": "2026-02-01T08:00:00Z", "target_sample": 30}}
```

### A/B Test Structure

**Hub: `hub/experiments/active-tests.json`**

```json
{
  "tests": [
    {
      "test_id": "test_resp_length_001",
      "created_at": "2026-02-01T08:00:00Z",
      "status": "running",
      "hypothesis": "Shorter responses improve task velocity without reducing quality",
      "variants": [
        {
          "variant_id": "v2_medium",
          "is_control": true,
          "directive": "Provide balanced detail - enough context, not overwhelming",
          "sample_size": 15,
          "avg_engagement": 7.8
        },
        {
          "variant_id": "v3_short",
          "is_control": false,
          "directive": "Target 1-3 sentences for simple answers. Expand only when complex.",
          "sample_size": 12,
          "avg_engagement": 8.1
        }
      ],
      "metrics": {
        "primary": "engagement_score",
        "secondary": ["task_completion_rate", "user_corrections", "follow_up_questions"]
      },
      "target_sample_size": 30,
      "confidence_threshold": 0.95,
      "spokes_assigned": {
        "framework": "v3_short",
        "client-api": "v2_medium",
        "personal-site": "v3_short"
      }
    }
  ],
  "completed_tests": [
    {
      "test_id": "test_comm_style_001",
      "completed_at": "2026-01-15T10:30:00Z",
      "winner": "v2",
      "result": "Direct/technical style increased engagement 23% vs formal",
      "promoted_to_production": true
    }
  ]
}
```

### Engagement Metrics

**Hub: `hub/learnings/persona.jsonl`**

```jsonl
{"timestamp": "2026-02-01T10:15:00Z", "spoke": "framework", "session_id": "sess_123", "variant_id": "v3_short", "engagement_score": 8, "task_completion": true, "user_corrections": 1, "follow_ups": 2, "session_duration": 1200, "llm_model": "claude-sonnet-4"}
{"timestamp": "2026-02-01T10:30:00Z", "spoke": "client-api", "session_id": "sess_124", "variant_id": "v2_medium", "engagement_score": 7, "task_completion": true, "user_corrections": 3, "follow_ups": 4, "session_duration": 1800, "llm_model": "gpt-4"}
```

## Flow: Hub → Spoke Teaching

### 1. Hub Generates Persona Directive

When teaching a spoke, hub creates `persona-directive.teaching`:

```json
{
  "for_spoke": "client-api",
  "generated_at": "2026-02-01T11:00:00Z",
  "persona_context": {
    "communication_style": {
      "directive": "Skip pleasantries. Dive into technical details immediately.",
      "tone": "professional-casual",
      "variant_id": "v2",
      "confidence": "high"
    },
    "code_style": {
      "directive": "Prefer explicit over implicit. Avoid one-liners if they reduce clarity.",
      "language_specific": {
        "python": "Use type hints, descriptive names, docstrings",
        "typescript": "Leverage strict mode, avoid 'any'"
      },
      "variant_id": "v1",
      "confidence": "high"
    },
    "response_format": {
      "directive": "Target 1-3 sentences for simple answers. Expand only when complex.",
      "variant_id": "v3_short",
      "ab_test": "test_resp_length_001",
      "is_experiment": true
    },
    "project_skillset": {
      "required_expertise": ["REST API design", "PostgreSQL", "Python async"],
      "mental_model": "Backend engineer focused on reliability and performance",
      "avoid": "Frontend frameworks, CSS discussions"
    }
  },
  "instructions_for_ai": [
    "Apply these persona directives to ALL interactions in this project",
    "Track engagement: note when user corrects tone/style",
    "Report metrics on closeout via WAI-Signals.jsonl",
    "If variant_id indicates A/B test, maintain consistency across session"
  ]
}
```

### 2. Spoke Receives & Applies

During closeout, spoke processes `persona-directive.teaching`:

```python
# In spoke_update.py
def _process_persona_directive(self, path: Path):
    directive = json.loads(path.read_text())
    
    # Update WAI-Point.json with persona context
    point = self.point_manager.load_point()
    point['persona_context'] = directive['persona_context']
    self.point_manager.save_point(point)
    
    # Update AGENTS.md with directives
    self._inject_persona_instructions(directive)
    
    # Archive directive in reference
    self._archive_teaching(path, "persona-directive")
```

### 3. AI Reads & Adapts

Next session, AI loads persona from WAI-Point.json or AGENTS.md:

```markdown
# Project: Client API

## Persona Context (Hub-Optimized)

**Communication Style:** Direct and technical (v2, high confidence)
- Skip pleasantries. Dive into technical details immediately.
- Professional-casual tone.

**Code Style:** Pythonic readability (v1, high confidence)
- Prefer explicit over implicit. Avoid one-liners if they reduce clarity.
- Use type hints, descriptive names, docstrings.

**Response Format:** Concise (v3_short, EXPERIMENT)
- Target 1-3 sentences for simple answers. Expand only when complex.
- NOTE: This is A/B test variant. Track engagement.

**Project Skillset:**
- Required: REST API design, PostgreSQL, Python async
- Mental model: Backend engineer focused on reliability and performance
- Avoid: Frontend frameworks, CSS discussions
```

### 4. Spoke Reports Metrics

On closeout, spoke adds engagement signal:

```jsonl
{"type": "engagement", "session_id": "sess_125", "variant_id": "v3_short", "engagement_score": 8, "task_completion": true, "user_corrections": 0, "notes": "User seemed satisfied with concise responses"}
```

### 5. Hub Learns & Promotes

Hub aggregates metrics, runs statistical analysis:

```python
# Pseudo-code for hub learning
def analyze_ab_test(test_id):
    metrics = load_metrics_for_test(test_id)
    control = metrics.filter(is_control=True)
    variant = metrics.filter(is_control=False)
    
    if variant.sample_size >= target_sample:
        p_value = statistical_test(control, variant)
        
        if p_value < 0.05 and variant.mean > control.mean:
            promote_variant(variant)
            create_new_persona_lug(variant)
            retire_old_variant(control)
```

## Engagement Scoring

### Automatic Metrics

- **Task Completion Rate:** Did session achieve goal?
- **User Corrections:** How often did user correct AI tone/style?
- **Follow-up Questions:** Indicator of clarity (fewer = better)
- **Session Duration:** Efficiency metric

### Explicit Feedback

User can rate engagement directly:

```bash
WAI rate session 8 --notes "Loved the concise style"
```

Adds to metrics:
```jsonl
{"type": "explicit_rating", "session_id": "sess_125", "score": 8, "notes": "Loved the concise style"}
```

## Variant Creation

### Manual Creation

```bash
WAI hub persona create \
  --title "Response Format: Ultra-Concise" \
  --directive "Max 2 sentences per response unless asked to elaborate" \
  --test-against "v3_short" \
  --metric engagement_score \
  --sample-size 20
```

### Automatic Exploration

Hub can auto-generate variants:

```python
def generate_variant(base_lug, exploration_strategy="moderate"):
    # Example: tone spectrum exploration
    if "professional-casual" in base_lug.directive:
        variants = [
            {"tone": "professional-formal", "hypothesis": "More formal might suit enterprise projects"},
            {"tone": "casual-friendly", "hypothesis": "More casual might improve creative projects"}
        ]
    return variants
```

## Cross-Model Compatibility

Persona directives work across different LLMs:

```json
{
  "directive": "Skip pleasantries. Dive into technical details immediately.",
  "model_adaptations": {
    "claude": "Works naturally with Claude's helpful tendency",
    "gpt": "Counteracts GPT's verbosity",
    "gemini": "Balances Gemini's academic tone"
  },
  "universal": true
}
```

## Best Practices

### DO
- ✅ Run one A/B test at a time per spoke
- ✅ Set minimum sample size (20-30 sessions)
- ✅ Track both quantitative and qualitative metrics
- ✅ Let tests run to completion before promoting
- ✅ Document winning variants with context

### DON'T
- ❌ Change variants mid-session (breaks consistency)
- ❌ Test too many variables simultaneously
- ❌ Promote variants without statistical confidence
- ❌ Ignore negative results (learning opportunity)
- ❌ Override hub directives without documenting why

## Implementation Phases

### Phase 1: Foundation
- [ ] Add persona lug type to lug system
- [ ] Create persona-directive teaching file structure
- [ ] Add persona context to WAI-Point.json
- [ ] Update AGENTS.md to include persona section

### Phase 2: Teaching Integration
- [ ] Hub generates persona directives during teach
- [ ] Spoke processes persona-directive.teaching
- [ ] AGENTS.md auto-updated with persona context
- [ ] Persona propagates to AI session start

### Phase 3: Metrics Collection
- [ ] Add engagement signal type to WAI-Signals.jsonl
- [ ] Closeout reports metrics to hub
- [ ] Hub aggregates metrics in learnings/persona.jsonl
- [ ] Dashboard shows engagement trends

### Phase 4: A/B Testing
- [ ] Hub creates and manages experiments
- [ ] Variants distributed to spokes
- [ ] Statistical analysis on collected metrics
- [ ] Automatic promotion of winning variants

### Phase 5: Self-Optimization
- [ ] Hub auto-generates variant hypotheses
- [ ] Continuous exploration of persona space
- [ ] Model-specific adaptations
- [ ] Cross-spoke pattern detection

## Example: Full Cycle

1. **Hub observes:** User often corrects AI for being too verbose
2. **Hub creates test:** "Concise vs Medium-length responses"
3. **Hub teaches spokes:** Distributes v3_short to framework, v2_medium to client-api
4. **AI adapts:** Each spoke's AI uses assigned variant
5. **Metrics collected:** 30 sessions later, v3_short has 8.1 avg engagement vs 7.8
6. **Hub promotes:** v3_short becomes new default
7. **Hub explores:** Creates v4_ultra_short to test further optimization
8. **Cycle repeats:** Continuous improvement

## Related Documentation

- [Hub-Spoke Unification](ARCHITECTURE-HUB-SPOKE-UNIFICATION.md)
- [Lug System](wai/lugs.py)
- [Teaching System](SESSION-COMPLETE-TEACHING-SYSTEM.md)
- [WAI-Point](wai/point.py)

---

**Pattern Type:** Self-Optimizing AI Collaboration  
**Status:** Specification (Not Yet Implemented)  
**Priority:** High (Revolutionary UX improvement)  
**Next Step:** Implement Phase 1 (persona lug type + WAI-Point integration)
