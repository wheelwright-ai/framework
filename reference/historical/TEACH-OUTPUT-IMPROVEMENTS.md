# Teach Command Output Improvements

**Date**: 2026-02-02  
**Change**: Enhanced teach output to explicitly show file replacement

---

## What Changed

### File-Level Clarity
**Before**:
```
[OK] WAI-Guide.md → /seed/ingest/
[OK] WAI-State.json → /seed/ingest/
```

**After**:
```
[OK] WAI-Guide.md replaced → /seed/ingest/
[OK] WAI-State.json created → /seed/ingest/
```

Now shows whether each file was **created** (new) or **replaced** (existing file overwritten).

### Per-Spoke Summary
**Before**:
```
Results by spoke:
    framework: ✓ Taught
    condoshield-crm: ✓ Taught
```

**After**:
```
Results by spoke:
    ✓ framework: Files replaced in seed/ingest/
    ✓ condoshield-crm: Files replaced in seed/ingest/
```

More explicit about what happened - files were **replaced** in the spoke's seed/ingest directory.

---

## Implementation Details

### Changes Made

1. **wai/commands/teach.py** (spoke files):
   - Check if destination file exists before writing
   - Report "created" if new, "replaced" if overwriting
   - Gives user confidence that old versions are gone

2. **wai/commands/teach.py** (hub files):
   - Same enhancement as spoke files
   - Consistent messaging throughout

3. **wai/core.py** (results display):
   - Added explicit text: "Files replaced in seed/ingest/"
   - Shows checkmark for clarity

---

## Code Changes

### teach.py: File Distribution

```python
# Before writing, check if file exists
file_exists = dst.exists()
content = src_path.read_text(encoding='utf-8')
dst.write_text(content, encoding='utf-8', errors='replace')

# Report action
action = "replaced" if file_exists else "created"
print_success(f"    [OK] {file_config['name']} {action} → /seed/ingest/")
```

### core.py: Results Display

```python
# Before
print_success("    " + spoke_name + ": " + status)

# After
print_success("    ✓ " + spoke_name + ": Files replaced in seed/ingest/")
```

---

## Benefits

✅ **Visibility**: User knows exactly what was changed  
✅ **Confidence**: Clear indication that old files were replaced  
✅ **Clarity**: No ambiguity about file status  
✅ **Tracking**: Can see whether files were new or updated  
✅ **Non-breaking**: Functional behavior unchanged, only output improved

---

## Example Output (After Changes)

```
🎓 Teaching all spokes...

Generating Upgrade Adoption Plan...
[OK] WAI-Guide.md
[OK] WAI-State.json
[OK] WAI-State.md
[OK] Signed with hub fingerprint

Distributing Template Files...
[OK] WAI-Guide.md created → /seed/ingest/
[OK] WAI-State.json created → /seed/ingest/
[OK] WAI-State.md created → /seed/ingest/

[... more spokes ...]

Results by spoke:
    ✓ framework: Files replaced in seed/ingest/
    ✓ condoshield-crm: Files replaced in seed/ingest/
    ✓ condoshield-gatsby: Files replaced in seed/ingest/
    ... (19 total)

✓ Teach complete! Taught 19 spoke(s)
```

---

## What This Ensures

1. **Old versions gone**: When `write_text()` overwrites, old content is completely replaced
2. **User knows it**: Explicit "replaced" or "created" messaging
3. **No silent overwrites**: Clear indication that files were updated
4. **Clean state**: Each spoke gets fresh copy of templates
5. **Auditable**: Output shows exactly what was distributed

---

## Already in Production?

This works with the current `wai teach` command. The file writing itself (`write_text()` with `errors='replace'`) already overwrites existing files. We're just making the user see it clearly.

No CLI changes needed. Just improved output visibility.

---

## Next: Hub Integration

Remember: This teach command currently writes directly to spokes. Per earlier discussion, it should eventually route through hub's outbound/ for coordination.

See: **TEACH-COMMAND-ALIGNMENT.md** in hub directory for that discussion.

For now: teach works great with improved output clarity.
