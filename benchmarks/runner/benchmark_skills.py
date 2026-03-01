#!/usr/bin/env python3
"""
WAI Skill-Based Architecture Benchmark

Measures the performance characteristics of the pure template/skill architecture
(no Python runtime, no database). Benchmarks what matters in the new model:

  1. Wakeup simulation  — read state + query open lugs
  2. Skill loading      — read all skill files, count sections
  3. Lug query speed    — filter WAI-Lugs.jsonl by status
  4. Session detection  — hook logic simulation
  5. Teach preparation  — enumerate skills for distribution

Run: python3 benchmarks/runner/benchmark_skills.py
"""
import json
import time
import statistics
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
COMMANDS = ROOT / "templates" / "commands"
WAI_SPOKE = ROOT / "WAI-Spoke"

# ─── Timing harness ───────────────────────────────────────────────────────────

def timeit(fn, runs: int = 20):
    """Run fn N times and return (median_ms, min_ms, max_ms)."""
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn()
        times.append((time.perf_counter() - t0) * 1000)
    return statistics.median(times), min(times), max(times)


# ─── Benchmarks ───────────────────────────────────────────────────────────────

def bench_wakeup_simulation():
    """
    Wakeup: read WAI-State.json + WAI-Lugs.jsonl, extract identity and open lugs.
    This is what an agent does on every session start.
    """
    state_file = WAI_SPOKE / "WAI-State.json"
    lugs_file = WAI_SPOKE / "WAI-Lugs.jsonl"

    def run():
        # Read project identity
        state = json.loads(state_file.read_text())
        name = state.get("wheel", {}).get("name", "")
        phase = state.get("wheel", {}).get("phase", "")
        # Read and filter open lugs
        open_lugs = []
        for line in lugs_file.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            lug = json.loads(line)
            if lug.get("s") in ("o", "open", "p", "in-progress"):
                open_lugs.append(lug)
        return name, phase, len(open_lugs)

    median, lo, hi = timeit(run)
    result = run()
    return {
        "name": "Wakeup simulation",
        "description": "Read WAI-State.json + query open lugs",
        "median_ms": round(median, 3),
        "min_ms": round(lo, 3),
        "max_ms": round(hi, 3),
        "result": f"project='{result[0]}', open_lugs={result[2]}",
    }


def bench_skill_loading():
    """
    Skill loading: read all skill .md files, count sections and lines.
    This simulates an agent loading its behavioral protocols.
    """
    skill_files = list(COMMANDS.glob("wai*.md"))

    def run():
        total_lines = 0
        total_sections = 0
        for sf in skill_files:
            content = sf.read_text()
            lines = content.count('\n')
            sections = content.count('\n## ')
            total_lines += lines
            total_sections += sections
        return total_lines, total_sections, len(skill_files)

    median, lo, hi = timeit(run)
    result = run()
    return {
        "name": "Skill loading",
        "description": f"Read {result[2]} skill files, count sections",
        "median_ms": round(median, 3),
        "min_ms": round(lo, 3),
        "max_ms": round(hi, 3),
        "result": f"{result[2]} skills, {result[0]} lines, {result[1]} sections",
    }


def bench_lug_query():
    """
    Lug query performance at scale — filter by type, status, impact.
    """
    lugs_file = WAI_SPOKE / "WAI-Lugs.jsonl"
    raw = lugs_file.read_text()

    def run_status_filter():
        lugs = [json.loads(l) for l in raw.splitlines() if l.strip()]
        return [l for l in lugs if l.get("s") in ("o", "open")]

    def run_type_filter():
        lugs = [json.loads(l) for l in raw.splitlines() if l.strip()]
        return [l for l in lugs if l.get("ty") in ("task", "bug", "feature")]

    def run_high_impact():
        lugs = [json.loads(l) for l in raw.splitlines() if l.strip()]
        return [l for l in lugs if int(l.get("impact", 0)) >= 8]

    med1, _, _ = timeit(run_status_filter)
    med2, _, _ = timeit(run_type_filter)
    med3, _, _ = timeit(run_high_impact)

    open_count = len(run_status_filter())
    task_count = len(run_type_filter())
    high_count = len(run_high_impact())
    total = sum(1 for l in raw.splitlines() if l.strip())

    return {
        "name": "Lug query performance",
        "description": f"Filter {total} lugs by status / type / impact",
        "queries": {
            "status_filter_ms": round(med1, 3),
            "type_filter_ms": round(med2, 3),
            "impact_filter_ms": round(med3, 3),
        },
        "result": f"{total} lugs: {open_count} open, {task_count} tasks, {high_count} high-impact",
    }


def bench_session_detection():
    """
    Session detection: simulate hook's jq-equivalent logic in Python.
    Is this a new session? (last_session_id == current_session_id?)
    """
    state_file = WAI_SPOKE / "WAI-State.json"

    def run():
        state = json.loads(state_file.read_text())
        session = state.get("_session_state", {})
        last_id = session.get("last_session_id", "")
        current_session = session.get("current_session") or {}
        current_id = current_session.get("session_id", "")
        is_new = (not current_id) or (last_id == current_id)
        protocol_done = session.get("protocol_completed", False)
        return is_new, protocol_done

    median, lo, hi = timeit(run)
    result = run()
    return {
        "name": "Session detection",
        "description": "Read state, detect new session vs continuation",
        "median_ms": round(median, 3),
        "min_ms": round(lo, 3),
        "max_ms": round(hi, 3),
        "result": f"new_session={result[0]}, protocol_done={result[1]}",
    }


def bench_teach_preparation():
    """
    Teach preparation: enumerate skills for distribution to spokes.
    What the hub does before pushing an upgrade-adoption-plan.
    """
    def run():
        skills = []
        for sf in COMMANDS.glob("wai*.md"):
            content = sf.read_text()
            title = content.split('\n')[0].lstrip('#').strip()
            size = len(content.encode())
            skills.append({
                "file": sf.name,
                "title": title,
                "size_bytes": size,
                "teaching_name": sf.name + ".teaching",
            })
        return sorted(skills, key=lambda x: x['file'])

    median, lo, hi = timeit(run)
    result = run()
    total_size = sum(s['size_bytes'] for s in result)
    return {
        "name": "Teach preparation",
        "description": "Enumerate skills, build distribution manifest",
        "median_ms": round(median, 3),
        "min_ms": round(lo, 3),
        "max_ms": round(hi, 3),
        "result": f"{len(result)} skills, {total_size/1024:.1f}KB total",
    }


# ─── Comparison: old vs new architecture ──────────────────────────────────────

def architecture_comparison():
    """
    Summary comparison: Python runtime (old) vs skill-based (new).
    """
    state_file = WAI_SPOKE / "WAI-State.json"
    lugs_file = WAI_SPOKE / "WAI-Lugs.jsonl"
    skills = list(COMMANDS.glob("wai*.md"))

    state_size = state_file.stat().st_size if state_file.exists() else 0
    lugs_size = lugs_file.stat().st_size if lugs_file.exists() else 0
    skills_size = sum(s.stat().st_size for s in skills)

    total_new = state_size + lugs_size + skills_size

    return {
        "old_architecture": {
            "description": "Python wai/ module (~55K lines) + wai-briefing.sh bash script",
            "runtime_required": True,
            "install_required": True,
            "estimated_load_time_ms": "200-500ms (Python import)",
        },
        "new_architecture": {
            "description": "Skills (markdown) + Lugs (JSONL) — read by agent directly",
            "runtime_required": False,
            "install_required": False,
            "context_files_kb": round(total_new / 1024, 1),
            "skills": len(skills),
        },
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\nWAI Skill-Based Architecture Benchmark")
    print(f"Framework: {ROOT}")
    print(f"Run at:    {datetime.now().isoformat()}")
    print(f"{'='*60}")

    results = []

    benchmarks = [
        bench_wakeup_simulation,
        bench_skill_loading,
        bench_session_detection,
        bench_teach_preparation,
    ]

    for bench in benchmarks:
        r = bench()
        results.append(r)
        median = r.get("median_ms", "—")
        lo = r.get("min_ms", "")
        hi = r.get("max_ms", "")
        print(f"\n  {r['name']}")
        print(f"    {r['description']}")
        if "queries" in r:
            q = r["queries"]
            print(f"    status_filter:  {q['status_filter_ms']:.3f}ms")
            print(f"    type_filter:    {q['type_filter_ms']:.3f}ms")
            print(f"    impact_filter:  {q['impact_filter_ms']:.3f}ms")
        else:
            print(f"    median: {median:.3f}ms  (min: {lo:.3f}ms, max: {hi:.3f}ms)")
        print(f"    → {r['result']}")

    # Lug query separately (has nested structure)
    lug_r = bench_lug_query()
    results.append(lug_r)
    q = lug_r["queries"]
    print(f"\n  {lug_r['name']}")
    print(f"    {lug_r['description']}")
    print(f"    status_filter:  {q['status_filter_ms']:.3f}ms")
    print(f"    type_filter:    {q['type_filter_ms']:.3f}ms")
    print(f"    impact_filter:  {q['impact_filter_ms']:.3f}ms")
    print(f"    → {lug_r['result']}")

    # Architecture comparison
    comp = architecture_comparison()
    print(f"\n{'='*60}")
    print(f"  Architecture Comparison")
    print(f"{'─'*60}")
    old = comp["old_architecture"]
    new = comp["new_architecture"]
    print(f"  OLD: {old['description']}")
    print(f"       Runtime required: {old['runtime_required']}")
    print(f"       Import time: {old['estimated_load_time_ms']}")
    print(f"  NEW: {new['description']}")
    print(f"       Runtime required: {new['runtime_required']}")
    print(f"       Context size: {new['context_files_kb']}KB ({new['skills']} skills)")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "benchmarks": results,
        "architecture_comparison": comp,
    }
    out_file = ROOT / "benchmarks" / "raw" / f"skills_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(output, indent=2))

    print(f"\n{'='*60}")
    print(f"  Results saved → {out_file.relative_to(ROOT)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
