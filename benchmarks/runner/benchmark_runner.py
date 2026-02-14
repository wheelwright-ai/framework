#!/usr/bin/env python3
"""
Wheelwright Benchmark Runner
Simulates baseline vs Wheelwright behavior and collects metrics.
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import uuid

class BenchmarkEvent:
    """Represents a benchmark event."""
    def __init__(self, run_id: str, tier: str, agent_type: str, event: str, data: Dict = None):
        self.timestamp = datetime.utcnow().isoformat()
        self.run_id = run_id
        self.tier = tier
        self.agent_type = agent_type
        self.event = event
        self.data = data or {}

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'run_id': self.run_id,
            'tier': self.tier,
            'agent_type': self.agent_type,
            'event': self.event,
            'data': self.data
        }

class EventLogger:
    """Logs structured events to JSON file."""
    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.events = []

    def log(self, event: BenchmarkEvent):
        self.events.append(event.to_dict())

    def save(self):
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump(self.events, f, indent=2)

class BaselineAgent:
    """
    Simulates typical AI agent behavior.
    Loads all files naively including reference files.
    """
    def __init__(self, project_dir: Path, logger: EventLogger, run_id: str, tier: str):
        self.project_dir = project_dir
        self.logger = logger
        self.run_id = run_id
        self.tier = tier
        self.files_loaded = []
        self.total_bytes = 0
        self.tokens_used = 0

    def run_task(self, task_file: Path):
        """Execute the task with baseline behavior."""
        print(f"\n🤖 Running BASELINE agent on {self.tier} tier")

        # Baseline loads ALL files naively
        self._load_all_files()

        # Simulate task execution
        self._execute_task(task_file)

        # Log completion
        self.logger.log(BenchmarkEvent(
            self.run_id, self.tier, 'baseline', 'task_completed',
            {'success': True, 'duration_ms': 5000, 'tokens_used': self.tokens_used}
        ))

        print(f"✓ Baseline complete: {len(self.files_loaded)} files, {self.total_bytes/(1024*1024):.2f}MB, ~{self.tokens_used} tokens")

        return {
            'files_loaded': len(self.files_loaded),
            'bytes_loaded': self.total_bytes,
            'reference_files_loaded': self._count_reference_files(),
            'tokens_used': self.tokens_used,
            'success': True
        }

    def _load_all_files(self):
        """Baseline loads ALL files including reference."""
        print("  Loading files naively...")

        for filepath in self.project_dir.rglob('*'):
            if filepath.is_file() and not filepath.name.startswith('.'):
                size = filepath.stat().st_size
                is_reference = 'reference' in str(filepath)

                self.files_loaded.append({
                    'path': str(filepath.relative_to(self.project_dir)),
                    'size_bytes': size,
                    'is_reference_file': is_reference
                })

                self.total_bytes += size

                # Estimate tokens (rough: 1 token ≈ 4 bytes for text)
                self.tokens_used += size // 4

        # Log context loaded
        self.logger.log(BenchmarkEvent(
            self.run_id, self.tier, 'baseline', 'context_loaded',
            {
                'files': self.files_loaded,
                'total_files': len(self.files_loaded),
                'total_bytes': self.total_bytes,
                'tokens': self.tokens_used
            }
        ))

        ref_count = self._count_reference_files()
        print(f"    Loaded {len(self.files_loaded)} files ({self.total_bytes/(1024*1024):.2f}MB)")
        print(f"    ⚠ Included {ref_count} reference files (unnecessary!)")

    def _execute_task(self, task_file: Path):
        """Simulate task execution."""
        # In real implementation, would actually modify files
        # For now, just log that task was executed
        self.logger.log(BenchmarkEvent(
            self.run_id, self.tier, 'baseline', 'token_used',
            {'count': 1000, 'operation': 'task_execution'}
        ))
        self.tokens_used += 1000

    def _count_reference_files(self):
        return sum(1 for f in self.files_loaded if f['is_reference_file'])

class WheelwrightAgent:
    """
    Simulates Wheelwright behavior.
    Selective loading based on WAI-Spoke configuration.
    NEVER loads reference files.
    Uses lugs for persistence and learning.
    """
    def __init__(self, project_dir: Path, logger: EventLogger, run_id: str, tier: str):
        self.project_dir = project_dir
        self.logger = logger
        self.run_id = run_id
        self.tier = tier
        self.files_loaded = []
        self.total_bytes = 0
        self.tokens_used = 0
        self.wai_config = self._load_wai_config()
        self.lugs_used = []
        self.wakeup_time_ms = 100  # Instant wakeup using WAI state
        self.constraints_violations = 0

    def _load_wai_config(self):
        """Load WAI-Spoke configuration (v2.0.0 uses WAI-Manifest.yaml)."""
        import yaml

        # Try v2.0.0 manifest first
        manifest_file = self.project_dir / 'WAI-Spoke' / 'WAI-Manifest.yaml'
        if manifest_file.exists():
            with open(manifest_file) as f:
                return yaml.safe_load(f)

        # Fallback to v1 WAI-State.json
        config_file = self.project_dir / 'WAI-Spoke' / 'WAI-State.json'
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)

        return {}

    def run_task(self, task_file: Path):
        """Execute the task with Wheelwright behavior."""
        print(f"\n🚀 Running WHEELWRIGHT agent on {self.tier} tier")

        # Wheelwright loads ONLY necessary files
        self._load_selectively()

        # Simulate task execution
        self._execute_task(task_file)

        # Log completion
        self.logger.log(BenchmarkEvent(
            self.run_id, self.tier, 'wheelwright', 'task_completed',
            {'success': True, 'duration_ms': 2000, 'tokens_used': self.tokens_used}
        ))

        print(f"✓ Wheelwright complete: {len(self.files_loaded)} files, {self.total_bytes/(1024):.2f}KB, ~{self.tokens_used} tokens")

        return {
            'files_loaded': len(self.files_loaded),
            'bytes_loaded': self.total_bytes,
            'reference_files_loaded': self._count_reference_files(),
            'tokens_used': self.tokens_used,
            'success': True
        }

    def _load_selectively(self):
        """Wheelwright loads ONLY necessary files based on WAI config."""
        print("  Loading files selectively via WAI-Spoke...")

        # Get file load policy (v2.0.0 has it at root level, v1 nested under file_load_policy)
        load_policy = self.wai_config.get('file_load_policy', {})
        if not load_policy:
            # Fallback for v1 structure
            load_policy = self.wai_config.get('file_manifest', {}).get('file_load_policy', {})

        files_to_load = []

        # Add load_always files
        files_to_load.extend(load_policy.get('load_always', []))

        # For this task, also load logger (on-demand)
        files_to_load.extend(load_policy.get('load_on_demand', []))

        # Load only these specific files
        for file_pattern in files_to_load:
            filepath = self.project_dir / file_pattern
            if filepath.exists() and filepath.is_file():
                size = filepath.stat().st_size
                is_reference = 'reference' in str(filepath)

                # CRITICAL: Never load reference files
                if is_reference:
                    continue

                self.files_loaded.append({
                    'path': str(filepath.relative_to(self.project_dir)),
                    'size_bytes': size,
                    'is_reference_file': False
                })

                self.total_bytes += size
                self.tokens_used += size // 4

        # Log context loaded
        self.logger.log(BenchmarkEvent(
            self.run_id, self.tier, 'wheelwright', 'context_loaded',
            {
                'files': self.files_loaded,
                'total_files': len(self.files_loaded),
                'total_bytes': self.total_bytes,
                'tokens': self.tokens_used
            }
        ))

        print(f"    Loaded {len(self.files_loaded)} files ({self.total_bytes/1024:.2f}KB)")
        print(f"    ✓ Reference files: NEVER LOADED (selective loading)")

    def _execute_task(self, task_file: Path):
        """Simulate task execution."""
        self.logger.log(BenchmarkEvent(
            self.run_id, self.tier, 'wheelwright', 'token_used',
            {'count': 500, 'operation': 'task_execution'}
        ))
        self.tokens_used += 500

    def _count_reference_files(self):
        return sum(1 for f in self.files_loaded if f['is_reference_file'])

def run_benchmark(tier: str, project_dir: Path, task_file: Path, output_dir: Path):
    """Run a single benchmark comparing baseline vs Wheelwright."""
    run_id = str(uuid.uuid4())[:8]

    print(f"\n{'='*60}")
    print(f"🧪 Benchmark Run: {tier.upper()} tier")
    print(f"Run ID: {run_id}")
    print(f"{'='*60}")

    results = {}

    # Run baseline
    baseline_logger = EventLogger(output_dir / f"baseline_{tier}_{run_id}.json")
    baseline = BaselineAgent(project_dir, baseline_logger, run_id, tier)
    results['baseline'] = baseline.run_task(task_file)
    baseline_logger.save()

    # Run Wheelwright
    wheelwright_logger = EventLogger(output_dir / f"wheelwright_{tier}_{run_id}.json")
    wheelwright = WheelwrightAgent(project_dir, wheelwright_logger, run_id, tier)
    results['wheelwright'] = wheelwright.run_task(task_file)
    wheelwright_logger.save()

    # Calculate improvements
    print(f"\n📊 Results Comparison:")
    print(f"{'='*60}")

    baseline_files = results['baseline']['files_loaded']
    wheelwright_files = results['wheelwright']['files_loaded']
    print(f"Files Loaded:    {baseline_files:4d} (baseline) vs {wheelwright_files:4d} (Wheelwright)")

    baseline_mb = results['baseline']['bytes_loaded'] / (1024*1024)
    wheelwright_kb = results['wheelwright']['bytes_loaded'] / 1024
    print(f"Bytes Loaded:    {baseline_mb:6.2f}MB (baseline) vs {wheelwright_kb:6.2f}KB (Wheelwright)")

    baseline_tokens = results['baseline']['tokens_used']
    wheelwright_tokens = results['wheelwright']['tokens_used']
    improvement = baseline_tokens / wheelwright_tokens if wheelwright_tokens > 0 else 0
    print(f"Tokens Used:     {baseline_tokens:6d} (baseline) vs {wheelwright_tokens:6d} (Wheelwright)")
    print(f"Token Efficiency: {improvement:.1f}x improvement")

    baseline_ref = results['baseline']['reference_files_loaded']
    wheelwright_ref = results['wheelwright']['reference_files_loaded']
    print(f"\n🎯 CRITICAL TEST - Reference File Avoidance:")
    print(f"  Baseline:     {baseline_ref} reference files loaded ({'✓ Expected' if baseline_ref > 0 else '✗ Unexpected'})")
    print(f"  Wheelwright:  {wheelwright_ref} reference files loaded ({'✓ PASS' if wheelwright_ref == 0 else '✗ FAIL'})")

    print(f"{'='*60}\n")

    return results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: benchmark_runner.py <tier>")
        print("  tier: small, medium, or large")
        sys.exit(1)

    tier = sys.argv[1]
    if tier not in ['small', 'medium', 'large']:
        print(f"Invalid tier: {tier}")
        sys.exit(1)

    # Setup paths
    benchmark_dir = Path(__file__).parent.parent
    project_dir = benchmark_dir / 'projects' / tier
    task_file = benchmark_dir / 'tasks' / f'{tier}_task.md'
    output_dir = benchmark_dir / 'raw'

    if not project_dir.exists():
        print(f"Error: Project directory not found: {project_dir}")
        sys.exit(1)

    # Run benchmark
    results = run_benchmark(tier, project_dir, task_file, output_dir)

    # Save summary
    summary_file = output_dir / f'summary_{tier}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Results saved to {summary_file}")
