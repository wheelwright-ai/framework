#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    WHEELWRIGHT PERFORMANCE BENCHMARK                          ║
║                                                                              ║
║  Measures: File Size · Query Speed · Update Speed · Token Efficiency         ║
║  Profiles: Small (50) · Medium (200) · Large (500) work items                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import sys
import time
import tempfile
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PROFILES = {
    "small": {"lugs": 50, "queries": 25, "updates": 10, "closeouts": 5},
    "medium": {"lugs": 200, "queries": 50, "updates": 25, "closeouts": 10},
    "large": {"lugs": 500, "queries": 100, "updates": 50, "closeouts": 20},
}

BENCHMARK_DIR = Path(__file__).parent / "benchmarks"
SPOKE_DIR = Path(__file__).parent / "WAI-Spoke"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProfileMetrics:
    profile: str
    lug_count: int
    
    # File Size (bytes)
    spoke_size_bytes: int = 0
    lugs_file_size_bytes: int = 0
    
    # Speed (seconds)
    avg_query_time_ms: float = 0.0
    avg_update_time_ms: float = 0.0
    avg_closeout_time_ms: float = 0.0
    total_queries: int = 0
    total_updates: int = 0
    total_closeouts: int = 0
    
    # Token Efficiency
    context_tokens: int = 0
    baseline_tokens: int = 0
    token_savings_percent: float = 0.0


@dataclass
class BenchmarkResult:
    version: str
    git_commit: str
    git_tag: Optional[str]
    timestamp: str
    platform: str
    python_version: str
    
    profiles: dict = field(default_factory=dict)
    
    # Aggregate scores (0-100)
    overall_score: float = 0.0
    file_size_score: float = 0.0
    speed_score: float = 0.0
    token_efficiency_score: float = 0.0
    
    # Comparison to previous run
    previous_run: Optional[str] = None
    delta_overall: Optional[float] = None
    callouts: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_git_info() -> tuple[str, Optional[str]]:
    """Get current git commit and tag."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], 
            stderr=subprocess.DEVNULL,
            cwd=Path(__file__).parent
        ).decode().strip()
    except Exception:
        commit = "unknown"
    
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--exact-match"],
            stderr=subprocess.DEVNULL,
            cwd=Path(__file__).parent
        ).decode().strip()
    except Exception:
        tag = None
    
    return commit, tag


def get_version() -> str:
    """Get version from package.json or WAI-State.json."""
    try:
        pkg = Path(__file__).parent / "package.json"
        if pkg.exists():
            return json.loads(pkg.read_text()).get("version", "1.0.0")
    except Exception:
        pass
    return "1.0.0"


def create_sample_lug(idx: int, closed: bool = False) -> dict:
    """Create a realistic sample Lug for benchmarking."""
    return {
        "id": f"LUG-{idx:05d}",
        "title": f"Sample work item {idx} with descriptive title",
        "status": "closed" if closed else "open",
        "priority": (idx % 5) + 1,
        "impact": (idx % 10) + 1,
        "created_at": datetime.now().isoformat(),
        "tags": ["benchmark", f"batch-{idx // 50}"],
        "description": f"This is a sample description for lug {idx}. " * 3,
        "dependencies": [f"LUG-{max(0, idx-1):05d}"] if idx > 0 else [],
    }


def measure_time(func, *args, iterations: int = 1) -> float:
    """Measure average execution time in milliseconds."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args)
        times.append((time.perf_counter() - start) * 1000)
    return sum(times) / len(times)


def calculate_tokens(text: str) -> int:
    """Approximate token count (4 chars ≈ 1 token)."""
    return len(text) // 4


def color(text: str, code: str) -> str:
    """ANSI color wrapper."""
    codes = {
        "green": "\033[92m", "red": "\033[91m", "yellow": "\033[93m",
        "blue": "\033[94m", "cyan": "\033[96m", "bold": "\033[1m",
        "dim": "\033[2m", "reset": "\033[0m"
    }
    return f"{codes.get(code, '')}{text}{codes['reset']}"


def delta_indicator(current: float, previous: float, lower_is_better: bool = True) -> str:
    """Show delta with color indicator."""
    if previous == 0:
        return ""
    
    delta = ((current - previous) / previous) * 100
    
    if lower_is_better:
        is_better = delta < 0
    else:
        is_better = delta > 0
    
    arrow = "↓" if delta < 0 else "↑"
    abs_delta = abs(delta)
    
    if abs_delta < 1:
        return color(f"({arrow}{abs_delta:.1f}%)", "dim")
    elif is_better:
        return color(f"({arrow}{abs_delta:.1f}%)", "green")
    else:
        return color(f"({arrow}{abs_delta:.1f}%)", "red")


# ═══════════════════════════════════════════════════════════════════════════════
# BENCHMARK TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class BenchmarkRunner:
    def __init__(self, profile_name: str, profile_config: dict):
        self.profile_name = profile_name
        self.config = profile_config
        self.temp_dir = None
        self.lugs_data = []
        
    def setup(self):
        """Create temporary spoke with sample data."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix=f"wai_bench_{self.profile_name}_"))
        
        # Create sample lugs (50% open, 50% closed)
        num_lugs = self.config["lugs"]
        self.lugs_data = [
            create_sample_lug(i, closed=(i < num_lugs // 2))
            for i in range(num_lugs)
        ]
        
        # Write to JSONL file
        lugs_file = self.temp_dir / "lugs.jsonl"
        with open(lugs_file, "w") as f:
            for lug in self.lugs_data:
                f.write(json.dumps(lug) + "\n")
        
        # Copy WAI-Spoke structure if exists
        if SPOKE_DIR.exists():
            for item in SPOKE_DIR.iterdir():
                if item.is_file():
                    shutil.copy(item, self.temp_dir / item.name)
        
    def teardown(self):
        """Clean up temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def measure_file_sizes(self) -> tuple[int, int]:
        """Measure spoke directory and lugs file sizes."""
        spoke_size = sum(f.stat().st_size for f in self.temp_dir.rglob("*") if f.is_file())
        lugs_file = self.temp_dir / "lugs.jsonl"
        lugs_size = lugs_file.stat().st_size if lugs_file.exists() else 0
        return spoke_size, lugs_size
    
    def benchmark_query(self) -> float:
        """Benchmark Lug query operations."""
        lugs_file = self.temp_dir / "lugs.jsonl"
        
        def query_open_high_priority():
            results = []
            with open(lugs_file) as f:
                for line in f:
                    lug = json.loads(line)
                    if lug["status"] == "open" and lug["priority"] <= 2:
                        results.append(lug)
            return results
        
        return measure_time(query_open_high_priority, iterations=self.config["queries"])
    
    def benchmark_update(self) -> float:
        """Benchmark Lug update operations."""
        lugs_file = self.temp_dir / "lugs.jsonl"
        
        def update_lug_status():
            lines = lugs_file.read_text().strip().split("\n")
            updated = []
            for line in lines:
                lug = json.loads(line)
                if lug["id"] == "LUG-00005":
                    lug["status"] = "in_progress"
                updated.append(json.dumps(lug))
            lugs_file.write_text("\n".join(updated) + "\n")
        
        return measure_time(update_lug_status, iterations=self.config["updates"])
    
    def benchmark_closeout(self) -> float:
        """Benchmark closeout operations (archive closed lugs)."""
        lugs_file = self.temp_dir / "lugs.jsonl"
        archive_file = self.temp_dir / "lugs-archive.jsonl"
        
        def closeout_session():
            lines = lugs_file.read_text().strip().split("\n")
            active = []
            archived = []
            
            for line in lines:
                lug = json.loads(line)
                if lug["status"] == "closed":
                    archived.append(line)
                else:
                    active.append(line)
            
            lugs_file.write_text("\n".join(active) + "\n")
            with open(archive_file, "a") as f:
                for line in archived:
                    f.write(line + "\n")
        
        return measure_time(closeout_session, iterations=min(3, self.config["closeouts"]))
    
    def measure_token_efficiency(self) -> tuple[int, int, float]:
        """Calculate token usage for context loading."""
        # Optimized: Load only open lugs
        open_lugs = [l for l in self.lugs_data if l["status"] == "open"]
        optimized_context = json.dumps(open_lugs)
        context_tokens = calculate_tokens(optimized_context)
        
        # Baseline: Load all lugs
        baseline_context = json.dumps(self.lugs_data)
        baseline_tokens = calculate_tokens(baseline_context)
        
        savings = ((baseline_tokens - context_tokens) / baseline_tokens * 100) if baseline_tokens > 0 else 0
        
        return context_tokens, baseline_tokens, savings
    
    def run(self) -> ProfileMetrics:
        """Run all benchmarks for this profile."""
        self.setup()
        
        try:
            spoke_size, lugs_size = self.measure_file_sizes()
            query_time = self.benchmark_query()
            update_time = self.benchmark_update()
            closeout_time = self.benchmark_closeout()
            context_tokens, baseline_tokens, savings = self.measure_token_efficiency()
            
            return ProfileMetrics(
                profile=self.profile_name,
                lug_count=self.config["lugs"],
                spoke_size_bytes=spoke_size,
                lugs_file_size_bytes=lugs_size,
                avg_query_time_ms=query_time,
                avg_update_time_ms=update_time,
                avg_closeout_time_ms=closeout_time,
                total_queries=self.config["queries"],
                total_updates=self.config["updates"],
                total_closeouts=self.config["closeouts"],
                context_tokens=context_tokens,
                baseline_tokens=baseline_tokens,
                token_savings_percent=savings,
            )
        finally:
            self.teardown()


# ═══════════════════════════════════════════════════════════════════════════════
# SCORING & COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_scores(profiles: dict[str, ProfileMetrics]) -> tuple[float, float, float, float]:
    """Calculate aggregate scores (0-100) from profile metrics."""
    
    # File Size Score: Lower is better, benchmark against expected sizes
    expected_sizes = {"small": 50_000, "medium": 200_000, "large": 500_000}
    size_scores = []
    for name, metrics in profiles.items():
        expected = expected_sizes.get(name, 100_000)
        ratio = min(1.0, expected / max(1, metrics.spoke_size_bytes))
        size_scores.append(ratio * 100)
    file_size_score = sum(size_scores) / len(size_scores)
    
    # Speed Score: Target <1ms query, <5ms update, <10ms closeout
    speed_scores = []
    for metrics in profiles.values():
        query_score = min(100, (1.0 / max(0.1, metrics.avg_query_time_ms)) * 100)
        update_score = min(100, (5.0 / max(0.5, metrics.avg_update_time_ms)) * 100)
        closeout_score = min(100, (10.0 / max(1, metrics.avg_closeout_time_ms)) * 100)
        speed_scores.append((query_score + update_score + closeout_score) / 3)
    speed_score = sum(speed_scores) / len(speed_scores)
    
    # Token Efficiency: Higher savings is better
    token_scores = [m.token_savings_percent for m in profiles.values()]
    token_score = sum(token_scores) / len(token_scores)
    
    # Overall: Weighted average
    overall = (file_size_score * 0.25) + (speed_score * 0.35) + (token_score * 0.40)
    
    return overall, file_size_score, speed_score, token_score


def load_previous_result() -> Optional[BenchmarkResult]:
    """Load the most recent benchmark result for comparison."""
    BENCHMARK_DIR.mkdir(exist_ok=True)
    
    results = sorted(BENCHMARK_DIR.glob("benchmark-*.json"), reverse=True)
    if results:
        try:
            data = json.loads(results[0].read_text())
            return BenchmarkResult(**data)
        except Exception:
            pass
    return None


def generate_callouts(current: BenchmarkResult, previous: Optional[BenchmarkResult]) -> list[str]:
    """Generate notable callouts for improvements/regressions."""
    callouts = []
    
    if not previous:
        callouts.append("🆕 First benchmark run - establishing baseline")
        return callouts
    
    # Overall score change
    if current.delta_overall:
        if current.delta_overall > 10:
            callouts.append(f"🚀 MAJOR IMPROVEMENT: Overall score up {current.delta_overall:.1f}%")
        elif current.delta_overall < -10:
            callouts.append(f"⚠️ REGRESSION: Overall score down {abs(current.delta_overall):.1f}%")
    
    # Profile-specific callouts
    for profile_name in PROFILES:
        if profile_name not in current.profiles or profile_name not in previous.profiles:
            continue
        
        curr = current.profiles[profile_name]
        prev = previous.profiles[profile_name]
        
        # Token efficiency
        token_delta = curr["token_savings_percent"] - prev["token_savings_percent"]
        if token_delta > 5:
            callouts.append(f"💡 {profile_name.upper()}: Token savings improved by {token_delta:.1f}%")
        elif token_delta < -5:
            callouts.append(f"⚠️ {profile_name.upper()}: Token savings dropped by {abs(token_delta):.1f}%")
        
        # Query speed
        if prev["avg_query_time_ms"] > 0:
            query_delta = ((curr["avg_query_time_ms"] - prev["avg_query_time_ms"]) / prev["avg_query_time_ms"]) * 100
            if query_delta < -20:
                callouts.append(f"⚡ {profile_name.upper()}: Queries {abs(query_delta):.0f}% faster")
            elif query_delta > 20:
                callouts.append(f"🐌 {profile_name.upper()}: Queries {query_delta:.0f}% slower")
    
    return callouts


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

def print_header():
    """Print benchmark header."""
    print()
    print(color("╔══════════════════════════════════════════════════════════════════════════════╗", "cyan"))
    print(color("║", "cyan") + color("              WHEELWRIGHT PERFORMANCE BENCHMARK                              ", "bold") + color("║", "cyan"))
    print(color("╚══════════════════════════════════════════════════════════════════════════════╝", "cyan"))
    print()


def print_system_info(result: BenchmarkResult):
    """Print system and version info."""
    print(color("  System Info", "bold"))
    print(color("  ───────────", "dim"))
    print(f"  Version:    {result.version}")
    print(f"  Git Commit: {result.git_commit}" + (f" ({result.git_tag})" if result.git_tag else ""))
    print(f"  Timestamp:  {result.timestamp}")
    print(f"  Platform:   {result.platform}")
    print(f"  Python:     {result.python_version}")
    print()


def print_profile_results(name: str, metrics: ProfileMetrics, prev_metrics: Optional[dict] = None):
    """Print results for a single profile."""
    title = f"  {name.upper()} Profile ({metrics.lug_count} work items)"
    print(color(title, "bold"))
    print(color("  " + "─" * (len(title) - 2), "dim"))
    
    # File Size
    size_kb = metrics.spoke_size_bytes / 1024
    prev_size = prev_metrics["spoke_size_bytes"] if prev_metrics else 0
    delta = delta_indicator(metrics.spoke_size_bytes, prev_size)
    print(f"  📁 Spoke Size:       {size_kb:>8.1f} KB  {delta}")
    
    lugs_kb = metrics.lugs_file_size_bytes / 1024
    print(f"  📄 Lugs File:        {lugs_kb:>8.1f} KB")
    
    # Speed
    prev_query = prev_metrics["avg_query_time_ms"] if prev_metrics else 0
    delta = delta_indicator(metrics.avg_query_time_ms, prev_query)
    print(f"  ⚡ Query Time:       {metrics.avg_query_time_ms:>8.2f} ms  {delta}")
    
    prev_update = prev_metrics["avg_update_time_ms"] if prev_metrics else 0
    delta = delta_indicator(metrics.avg_update_time_ms, prev_update)
    print(f"  ✏️  Update Time:      {metrics.avg_update_time_ms:>8.2f} ms  {delta}")
    
    prev_closeout = prev_metrics["avg_closeout_time_ms"] if prev_metrics else 0
    delta = delta_indicator(metrics.avg_closeout_time_ms, prev_closeout)
    print(f"  📦 Closeout Time:    {metrics.avg_closeout_time_ms:>8.2f} ms  {delta}")
    
    # Token Efficiency
    prev_savings = prev_metrics["token_savings_percent"] if prev_metrics else 0
    delta = delta_indicator(metrics.token_savings_percent, prev_savings, lower_is_better=False)
    print(f"  🎯 Token Savings:    {metrics.token_savings_percent:>8.1f}%   {delta}")
    print(f"     ({metrics.context_tokens:,} vs {metrics.baseline_tokens:,} baseline)")
    print()


def print_overall_scores(result: BenchmarkResult, previous: Optional[BenchmarkResult] = None):
    """Print overall scores."""
    print(color("  ══════════════════════════════════════════════════════════════════════", "cyan"))
    print(color("  OVERALL SCORES", "bold"))
    print(color("  ══════════════════════════════════════════════════════════════════════", "cyan"))
    
    prev_overall = previous.overall_score if previous else 0
    prev_size = previous.file_size_score if previous else 0
    prev_speed = previous.speed_score if previous else 0
    prev_token = previous.token_efficiency_score if previous else 0
    
    delta = delta_indicator(result.overall_score, prev_overall, lower_is_better=False)
    print(f"  🏆 Overall:          {result.overall_score:>6.1f} / 100  {delta}")
    
    delta = delta_indicator(result.file_size_score, prev_size, lower_is_better=False)
    print(f"  📁 File Size:        {result.file_size_score:>6.1f} / 100  {delta}")
    
    delta = delta_indicator(result.speed_score, prev_speed, lower_is_better=False)
    print(f"  ⚡ Speed:            {result.speed_score:>6.1f} / 100  {delta}")
    
    delta = delta_indicator(result.token_efficiency_score, prev_token, lower_is_better=False)
    print(f"  🎯 Token Efficiency: {result.token_efficiency_score:>6.1f} / 100  {delta}")
    print()


def print_callouts(callouts: list[str]):
    """Print notable callouts."""
    if not callouts:
        return
    
    print(color("  CALLOUTS", "bold"))
    print(color("  ────────", "dim"))
    for callout in callouts:
        print(f"  {callout}")
    print()


def print_footer(log_path: Path):
    """Print footer with log file location."""
    print(color("  ──────────────────────────────────────────────────────────────────────", "dim"))
    print(f"  📊 Results saved to: {log_path.name}")
    print(f"  💡 Run with --compare to see history")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def run_benchmark(save: bool = True, tag: bool = False) -> BenchmarkResult:
    """Run the full benchmark suite."""
    
    print_header()
    
    # Get system info
    version = get_version()
    git_commit, git_tag = get_git_info()
    timestamp = datetime.now().isoformat()
    platform = f"{sys.platform}"
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Load previous for comparison
    previous = load_previous_result()
    
    # Create result object
    result = BenchmarkResult(
        version=version,
        git_commit=git_commit,
        git_tag=git_tag,
        timestamp=timestamp,
        platform=platform,
        python_version=python_version,
        previous_run=previous.timestamp if previous else None,
    )
    
    # Print system info
    print_system_info(result)
    
    # Run each profile
    print(color("  Running Benchmarks...", "bold"))
    print()
    
    for profile_name, profile_config in PROFILES.items():
        print(f"  ⏳ Running {profile_name} profile...", end=" ", flush=True)
        runner = BenchmarkRunner(profile_name, profile_config)
        metrics = runner.run()
        result.profiles[profile_name] = asdict(metrics)
        print(color("✓", "green"))
    
    print()
    
    # Calculate scores
    overall, file_size, speed, token = calculate_scores(
        {k: ProfileMetrics(**v) for k, v in result.profiles.items()}
    )
    result.overall_score = overall
    result.file_size_score = file_size
    result.speed_score = speed
    result.token_efficiency_score = token
    
    # Calculate delta
    if previous:
        result.delta_overall = ((overall - previous.overall_score) / previous.overall_score * 100) if previous.overall_score > 0 else 0
    
    # Generate callouts
    result.callouts = generate_callouts(result, previous)
    
    # Print results
    for profile_name in PROFILES:
        prev_metrics = previous.profiles.get(profile_name) if previous else None
        print_profile_results(
            profile_name, 
            ProfileMetrics(**result.profiles[profile_name]),
            prev_metrics
        )
    
    print_overall_scores(result, previous)
    print_callouts(result.callouts)
    
    # Save results
    if save:
        BENCHMARK_DIR.mkdir(exist_ok=True)
        log_filename = f"benchmark-{timestamp.replace(':', '-').replace('T', '_')[:19]}.json"
        log_path = BENCHMARK_DIR / log_filename
        log_path.write_text(json.dumps(asdict(result), indent=2))
        print_footer(log_path)
        
        # Create git tag if requested
        if tag:
            tag_name = f"benchmark-v{version}-{timestamp[:10]}"
            try:
                subprocess.run(["git", "tag", tag_name], check=True, capture_output=True, cwd=Path(__file__).parent)
                print(f"  🏷️  Git tag created: {tag_name}")
            except Exception as e:
                print(f"  ⚠️  Failed to create git tag: {e}")
    
    return result


def show_history():
    """Show benchmark history."""
    BENCHMARK_DIR.mkdir(exist_ok=True)
    results = sorted(BENCHMARK_DIR.glob("benchmark-*.json"))
    
    if not results:
        print("  No benchmark history found.")
        return
    
    print()
    print(color("  BENCHMARK HISTORY", "bold"))
    print(color("  " + "═" * 72, "cyan"))
    print(f"  {'Date':<20} {'Version':<10} {'Commit':<10} {'Score':>8} {'Δ':>8}")
    print(color("  " + "─" * 72, "dim"))
    
    prev_score = None
    for result_path in results:
        try:
            data = json.loads(result_path.read_text())
            date = data["timestamp"][:10]
            version = data["version"]
            commit = data["git_commit"][:8]
            score = data["overall_score"]
            
            delta = ""
            if prev_score is not None:
                d = score - prev_score
                if d > 0:
                    delta = color(f"+{d:.1f}", "green")
                elif d < 0:
                    delta = color(f"{d:.1f}", "red")
                else:
                    delta = color("0.0", "dim")
            
            print(f"  {date:<20} {version:<10} {commit:<10} {score:>8.1f} {delta:>8}")
            prev_score = score
        except Exception:
            continue
    
    print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Wheelwright Performance Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmark.py              Run benchmark and save results
  python benchmark.py --tag        Run benchmark and create git tag
  python benchmark.py --history    Show benchmark history
  python benchmark.py --no-save    Run benchmark without saving
        """
    )
    parser.add_argument("--tag", action="store_true", help="Create git tag for this run")
    parser.add_argument("--history", action="store_true", help="Show benchmark history")
    parser.add_argument("--no-save", action="store_true", help="Don't save results")
    
    args = parser.parse_args()
    
    if args.history:
        show_history()
    else:
        run_benchmark(save=not args.no_save, tag=args.tag)


if __name__ == "__main__":
    main()
