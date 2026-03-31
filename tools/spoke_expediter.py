#!/usr/bin/env python3
"""
Spoke-Local Expediter — Lug Quality Scorer + Signal Triage

Scores all active lugs on PEV completeness (0-10), generates a priority-ordered
refinement queue, and optionally triages undelivered signals with categorization
and quality scoring.

Usage:
    python3 tools/spoke_expediter.py                       # Score lugs only
    python3 tools/spoke_expediter.py --signals             # Score lugs + triage signals
    python3 tools/spoke_expediter.py --top 5 --threshold 6 # Custom display
    python3 tools/spoke_expediter.py --spoke-path /other   # Different spoke
"""

import json
import os
import glob
import argparse
import re
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Field accessors (handles both full and compact lug schemas)
# ---------------------------------------------------------------------------

def get_id(lug):
    return lug.get("id") or lug.get("i") or os.path.basename(lug.get("_filepath", "unknown")).replace(".json", "")

def get_title(lug):
    return lug.get("title") or lug.get("t") or get_id(lug)

def get_type(lug):
    return lug.get("type") or lug.get("ty") or "unknown"

def get_status(lug):
    return lug.get("status") or lug.get("s") or "unknown"


# ---------------------------------------------------------------------------
# Lug Quality Scoring (10-point PEV rubric — matches hub Expediter)
# ---------------------------------------------------------------------------

SKIP_TYPES = {"epic", "e", "signal", "s", "idea", "policy", "audit", "directive", "session-summary"}

def score_lug_quality(lug):
    """Score a lug on PEV completeness. Returns (score, missing_fields). Max: 10."""
    score = 0
    missing = []

    perceive = lug.get("perceive") or lug.get("p") or ""
    if len(str(perceive).strip()) > 10:
        score += 2
    else:
        missing.append("perceive")

    execute = lug.get("execute") or lug.get("e") or ""
    if len(str(execute).strip()) > 100:
        score += 2
    elif execute:
        score += 1
        missing.append("execute_too_vague")
    else:
        missing.append("execute")

    verify = lug.get("verify") or lug.get("v") or ""
    if len(str(verify).strip()) > 10:
        score += 2
    else:
        missing.append("verify")

    ac = lug.get("acceptance_criteria") or lug.get("ac") or []
    if isinstance(ac, list) and len(ac) > 0:
        score += 2
    else:
        missing.append("acceptance_criteria")

    tf = lug.get("target_files") or lug.get("tf") or []
    if isinstance(tf, list) and len(tf) > 0:
        score += 1
    else:
        missing.append("target_files")

    model_fit = (lug.get("model_fit") or lug.get("mf") or "").upper()
    if model_fit == "HAIKU":
        score += 1
    elif not model_fit:
        missing.append("model_fit_unset")

    return score, missing


def get_roi(lug):
    """Extract ROI from lug. Compute as impact/effort if roi not present."""
    roi = lug.get("roi")
    if roi is not None:
        return float(roi)
    impact = float(lug.get("impact", 5))
    effort = float(lug.get("effort", 5))
    return impact / effort if effort > 0 else impact


def suggest_improvements(lug, missing_fields):
    """Generate targeted improvement suggestions."""
    suggestions = []
    if "perceive" in missing_fields:
        suggestions.append("Add perceive: list specific files/state to read before starting")
    if "execute" in missing_fields:
        suggestions.append("Add execute: step-by-step instructions (3+ concrete steps)")
    elif "execute_too_vague" in missing_fields:
        suggestions.append("Expand execute: too brief — add specific commands/file edits")
    if "verify" in missing_fields:
        suggestions.append("Add verify: exact commands to confirm success")
    if "acceptance_criteria" in missing_fields:
        suggestions.append("Add acceptance_criteria: 2-4 testable conditions")
    if "target_files" in missing_fields:
        suggestions.append("Add target_files: exact file paths to create/modify")
    if "model_fit_unset" in missing_fields:
        suggestions.append("Set model_fit: HAIKU/SONNET/OPUS — cheapest capable model")
    elif (lug.get("model_fit") or "").upper() == "OPUS":
        suggestions.append("Review model_fit: can this be SONNET? Add specificity to push down")
    return suggestions


# ---------------------------------------------------------------------------
# Lug Scanning
# ---------------------------------------------------------------------------

def scan_lugs(spoke_path):
    """Scan active lugs (open + in_progress), skipping non-dispatchable types."""
    lugs = []
    for status in ("open", "in_progress"):
        pattern = os.path.join(spoke_path, "WAI-Spoke", "lugs", "bytype", "*", status, "*.json")
        for filepath in glob.glob(pattern):
            try:
                with open(filepath) as f:
                    lug = json.load(f)
                lug["_filepath"] = filepath
                ty = get_type(lug)
                if ty in SKIP_TYPES:
                    continue
                lugs.append(lug)
            except (json.JSONDecodeError, IOError):
                pass
    return lugs


# ---------------------------------------------------------------------------
# Signal Triage
# ---------------------------------------------------------------------------

SIGNAL_CATEGORIES = {
    "architectural": ["architecture", "design", "hub", "spoke", "advisor", "protocol", "schema",
                      "lug", "skill", "template", "migration", "canonical", "structure"],
    "operational": ["deploy", "cron", "nightly", "gardener", "tender", "health", "remediat",
                    "monitor", "uptime", "availability", "ci", "cd", "pipeline"],
    "ai-guidance": ["model", "haiku", "sonnet", "opus", "routing", "context", "token",
                    "prompt", "agent", "dispatch", "ozi", "claude", "gemini"],
    "performance": ["speed", "latency", "cache", "optim", "throughput", "cost", "efficient"],
    "security": ["auth", "permission", "secret", "encrypt", "sanitiz", "pii", "credential"],
    "workflow": ["session", "closeout", "wakeup", "teaching", "signal", "lug", "track",
                 "foundation", "process", "lifecycle"],
}

def categorize_signal(signal):
    """Assign a category based on keyword matching in title + signal + rationale."""
    text = " ".join([
        str(signal.get("title", "")),
        str(signal.get("signal", "")),
        str(signal.get("rationale", "")),
        str(signal.get("description", "")),
    ]).lower()

    scores = {}
    for category, keywords in SIGNAL_CATEGORIES.items():
        scores[category] = sum(1 for kw in keywords if kw in text)

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "reference"
    return best


def score_signal_quality(signal):
    """Score signal quality: 0-3 (has clear title + signal/description + rationale)."""
    score = 0
    if len(str(signal.get("title", "")).strip()) > 5:
        score += 1
    body = str(signal.get("signal", "") or signal.get("description", "")).strip()
    if len(body) > 20:
        score += 1
    if len(str(signal.get("rationale", "")).strip()) > 10:
        score += 1
    return score


def assess_scope(signal):
    """Assess signal scope: spoke-local, framework, hub, or multi-spoke."""
    text = " ".join([
        str(signal.get("title", "")),
        str(signal.get("signal", "")),
        str(signal.get("rationale", "")),
        str(signal.get("description", "")),
    ]).lower()

    if any(w in text for w in ["all spoke", "every spoke", "fleet", "cross-spoke", "multi-spoke"]):
        return "multi-spoke"
    if any(w in text for w in ["hub", "registry", "distribution", "kb pattern", "fleet"]):
        return "hub"
    if any(w in text for w in ["framework", "template", "teaching", "skill system", "protocol"]):
        return "framework"
    return "spoke-local"


def is_teaching_candidate(signal):
    """Does this signal encode a procedural rule that should become a teaching?"""
    text = " ".join([
        str(signal.get("signal", "")),
        str(signal.get("rationale", "")),
        str(signal.get("description", "")),
    ]).lower()
    rule_markers = ["always", "never", "must", "should", "rule", "pattern", "prevent",
                    "ensure", "enforce", "gate", "guard", "require"]
    return sum(1 for m in rule_markers if m in text) >= 2


def scan_signals(spoke_path):
    """Scan undelivered signals."""
    signals = []
    pattern = os.path.join(spoke_path, "WAI-Spoke", "lugs", "bytype", "signal", "undelivered", "*.json")
    for filepath in glob.glob(pattern):
        try:
            with open(filepath) as f:
                sig = json.load(f)
            sig["_filepath"] = filepath
            signals.append(sig)
        except (json.JSONDecodeError, IOError):
            pass
    return signals


def triage_signals(signals):
    """Triage signals: categorize, score quality, assess scope."""
    results = []
    for sig in signals:
        results.append({
            "id": get_id(sig),
            "title": get_title(sig)[:80],
            "impact": sig.get("impact", 0),
            "category": categorize_signal(sig),
            "quality": score_signal_quality(sig),
            "scope": assess_scope(sig),
            "teaching_candidate": is_teaching_candidate(sig),
            "filepath": sig.get("_filepath", ""),
            "triaged_at": now(),
        })
    results.sort(key=lambda x: (-x["impact"], -x["quality"]))
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Spoke-Local Expediter: Lug Quality + Signal Triage")
    parser.add_argument("--spoke-path", default=".", help="Path to spoke root (default: current dir)")
    parser.add_argument("--top", type=int, default=15, help="Number of top items to display")
    parser.add_argument("--threshold", type=int, default=6, help="Quality score threshold (<=N = needs refinement)")
    parser.add_argument("--signals", action="store_true", help="Also triage undelivered signals")
    args = parser.parse_args()

    spoke_path = os.path.abspath(args.spoke_path)
    advisor_dir = os.path.join(spoke_path, "WAI-Spoke", "advisors", "expediter")
    os.makedirs(advisor_dir, exist_ok=True)

    print("Spoke Expediter — Lug Quality Scorer + Signal Triage")
    print(f"Spoke: {os.path.basename(spoke_path)}")
    print("=" * 70)

    # ── Lug Scoring ─────────────────────────────────────────────────────
    lugs = scan_lugs(spoke_path)
    print(f"\nLugs scanned: {len(lugs)} (excluding epics/signals/ideas)")

    scored = []
    for lug in lugs:
        quality, missing = score_lug_quality(lug)
        roi = get_roi(lug)
        dispatch_priority = roi * (10 - quality)

        scored.append({
            "id": get_id(lug),
            "title": get_title(lug)[:80],
            "type": get_type(lug),
            "quality_score": quality,
            "roi": round(roi, 2),
            "dispatch_priority": round(dispatch_priority, 2),
            "missing_fields": missing,
            "model_fit": (lug.get("model_fit") or lug.get("mf") or "unset"),
            "suggestions": suggest_improvements(lug, missing),
            "filepath": lug.get("_filepath", ""),
            "scored_at": now(),
        })

    scored.sort(key=lambda x: x["dispatch_priority"], reverse=True)
    needs_refinement = [s for s in scored if s["quality_score"] <= args.threshold]
    acceptable = [s for s in scored if s["quality_score"] > args.threshold]

    # Quality distribution
    dist = {}
    for s in scored:
        q = s["quality_score"]
        dist[q] = dist.get(q, 0) + 1
    print(f"\nQuality distribution:")
    for q in sorted(dist.keys()):
        bar = "█" * dist[q]
        label = "✗" if q <= args.threshold else "✓"
        print(f"  {q:2d}/10 {label} {bar} ({dist[q]})")
    print(f"\n  Needs refinement (≤{args.threshold}): {len(needs_refinement)}")
    print(f"  Acceptable (>{args.threshold}): {len(acceptable)}")

    # Write refinement queue
    queue_path = os.path.join(advisor_dir, "refinement-queue.jsonl")
    with open(queue_path, "w") as f:
        for item in scored:  # Write all scored items, sorted by priority
            f.write(json.dumps(item) + "\n")

    # Display top targets
    top_n = min(args.top, len(needs_refinement))
    if top_n > 0:
        print(f"\nTop {top_n} refinement targets:")
        print(f"  {'ID':<42} {'ROI':>5} {'Q':>3} {'Pri':>7} {'Missing'}")
        print(f"  {'-'*80}")
        for item in needs_refinement[:top_n]:
            missing_str = ", ".join(item["missing_fields"][:3])
            print(f"  {item['id']:<42} {item['roi']:>5.1f} {item['quality_score']:>3} {item['dispatch_priority']:>7.1f}  {missing_str}")

    # ── Signal Triage ───────────────────────────────────────────────────
    signal_results = []
    if args.signals:
        signals = scan_signals(spoke_path)
        print(f"\n{'='*70}")
        print(f"Signal Triage: {len(signals)} undelivered signals")

        if signals:
            signal_results = triage_signals(signals)

            # Category summary
            cats = {}
            for s in signal_results:
                cats[s["category"]] = cats.get(s["category"], 0) + 1
            print(f"\nCategories: {', '.join(f'{c}={n}' for c, n in sorted(cats.items()))}")

            teaching_count = sum(1 for s in signal_results if s["teaching_candidate"])
            if teaching_count:
                print(f"Teaching candidates: {teaching_count}")

            print(f"\n  {'ID':<42} {'Impact':>6} {'Q':>3} {'Category':<15} {'Scope':<12} {'Teach'}")
            print(f"  {'-'*95}")
            for s in signal_results:
                teach = "→teach" if s["teaching_candidate"] else ""
                print(f"  {s['id']:<42} {s['impact']:>6} {s['quality']:>3} {s['category']:<15} {s['scope']:<12} {teach}")
        else:
            print("  No undelivered signals.")

    # ── Update State ────────────────────────────────────────────────────
    state_path = os.path.join(advisor_dir, "scan_state.json")
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)
    else:
        state = {
            "advisor_id": "expediter",
            "advisor_name": "Spoke-Local Expediter",
            "version": "1.0.0",
            "initialized_at": now(),
            "stats": {},
        }

    state["last_run_at"] = now()
    state["refinement_queue_size"] = len(needs_refinement)
    stats = state.setdefault("stats", {})
    stats["lugs_scored"] = stats.get("lugs_scored", 0) + len(scored)
    stats["runs"] = stats.get("runs", 0) + 1
    stats["last_quality_avg"] = round(sum(s["quality_score"] for s in scored) / max(len(scored), 1), 1)
    stats["last_needs_refinement"] = len(needs_refinement)
    if signal_results:
        stats["signals_triaged"] = stats.get("signals_triaged", 0) + len(signal_results)
        stats["teaching_candidates_found"] = sum(1 for s in signal_results if s["teaching_candidate"])

    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

    # ── Summary ─────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"EXPEDITER COMPLETE")
    print(f"  Lugs scored: {len(scored)}  |  Needs refinement: {len(needs_refinement)}  |  Avg quality: {stats['last_quality_avg']}/10")
    if signal_results:
        print(f"  Signals triaged: {len(signal_results)}  |  Teaching candidates: {stats.get('teaching_candidates_found', 0)}")
    print(f"  Queue: {queue_path}")
    print(f"  State: {state_path}")


if __name__ == "__main__":
    main()
