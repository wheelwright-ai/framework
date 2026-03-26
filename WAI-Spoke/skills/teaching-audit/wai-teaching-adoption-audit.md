# WAI Teaching Adoption Audit

## Purpose

Verify that teachings in `seed/ingest/processed/` were actually adopted, not just moved.

## Audit Protocol

### For Each Teaching File in processed/:

1. **Read the teaching** — extract the "Changes to Make" or "How to Apply" section
2. **Identify target file** — what file should this teaching have modified?
3. **Find verification fingerprint** — each teaching must include one (unique string, code marker, or filename)
   - If teaching says "Search for: `Do NOT skip silently`" → grep for that text
   - If teaching says "Create file: `wai-improve-reference.md`" → check if file exists
   - If teaching says "Add field: `routed_to`" → grep for that field in target
4. **Verify fingerprint exists** — if found: PASS, if not found: FAIL
5. **Report result**:
   - PASS: Teaching was adopted ✓
   - FAIL: Teaching was processed but not adopted ✗ (mark for re-review)

### Remediation (If Teaching Fails Audit)

If a teaching fails verification:
1. **Re-read the original teaching** (don't just trust processed/ copy — re-fetch from hub if available)
2. **Apply the prescribed changes manually**
3. **Re-run verification** to confirm
4. **Document as signal**: "Teaching {id} was processed but not adopted on {date}. Now corrected."

### At Wakeup

Add a new substep to Wakeup Step 7 (Display Briefing):

```
## Step 7a: Teaching Adoption Audit (on first session)

IF this is your first session since receiving this teaching:
  FOR EACH file in WAI-Spoke/seed/ingest/processed/:
    Run verification fingerprint check
    IF verification fails:
      Surface in briefing: "⚠️ {teaching-name} processed but not adopted — re-review required"
      Keep teaching in briefing for user attention
  Report summary: "Teaching audit: N passed, M failed"

IF no failures:
  Report: "Teaching audit: all N teachings verified ✓"
```

### Future Teaching Requirements

**Every teaching MUST include a machine-checkable verification fingerprint** in its "Changes to Make" section.

Examples:
```
Search for this text to verify adoption:
  "Do NOT skip silently" (in wai.md Step 5)

Or verify this file was created:
  "wai-improve-reference.md" (in templates/commands/)

Or grep for this field:
  "routed_to.*local.*framework.*signal" (in lug JSON)
```

If teaching cannot provide a verification fingerprint, it should be re-written.
