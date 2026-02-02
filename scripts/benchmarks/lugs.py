#!/usr/bin/env python3
"""
Performance benchmark script for Lug system.

Creates 100 Lugs, closes 50, and measures:
- Active file size
- Load time
- Estimated context tokens
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wai.lugs import LugManager


def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 chars per token."""
    return len(text) // 4


def benchmark_lug_performance(spoke_dir: Path):
    """Run comprehensive Lug performance benchmark."""
    
    print("=" * 60)
    print("LUG PERFORMANCE BENCHMARK")
    print("=" * 60)
    print()
    
    # Initialize manager
    print("[1/6] Initializing LugManager...")
    start_time = time.time()
    manager = LugManager(spoke_dir)
    init_time = time.time() - start_time
    print(f"✓ Initialized in {init_time:.4f}s")
    print()
    
    # Create 100 Lugs
    print("[2/6] Creating 100 Lugs...")
    lug_types = ['epic', 'issue', 'bug', 'work', 'ask']
    priorities = ['low', 'medium', 'high']
    impacts = ['small', 'medium', 'large']
    
    created_lugs = []
    create_start = time.time()
    
    for i in range(100):
        lug = manager.create_lug(
            title=f"Benchmark Lug {i+1}: {lug_types[i % len(lug_types)]} item",
            lug_type=lug_types[i % len(lug_types)],
            priority=priorities[i % len(priorities)],
            impact=impacts[i % len(impacts)],
            value=(i % 10) + 1,
            justification=f"Performance test iteration {i+1}",
            origin="benchmark:automated",
            extras={'benchmark_id': i, 'batch': 'perf_test_001'}
        )
        created_lugs.append(lug)
        
        if (i + 1) % 25 == 0:
            print(f"  Created {i+1}/100 Lugs...")
    
    create_time = time.time() - create_start
    print(f"✓ Created 100 Lugs in {create_time:.4f}s ({create_time/100*1000:.2f}ms per Lug)")
    print()
    
    # Add some dependencies
    print("[3/6] Adding dependency relationships...")
    dep_start = time.time()
    for i in range(0, 20, 2):
        if i + 1 < len(created_lugs):
            manager.add_dependency(
                created_lugs[i].id[:8],
                created_lugs[i + 1].id[:8]
            )
    dep_time = time.time() - dep_start
    print(f"✓ Added 10 dependency relationships in {dep_time:.4f}s")
    print()
    
    # Close 50 Lugs
    print("[4/6] Closing 50 Lugs...")
    close_start = time.time()
    
    for i in range(50):
        # Skip lugs with dependencies for simplicity
        lug = created_lugs[i + 50]
        if not lug.deps and not lug.blocked_by:
            manager.close_lug(
                lug.id[:8],
                summary=f"Benchmark closure {i+1}",
                resolved_by={'type': 'benchmark', 'iteration': i},
                skip_policy_check=True
            )
        
        if (i + 1) % 25 == 0:
            print(f"  Closed {i+1}/50 Lugs...")
    
    close_time = time.time() - close_start
    print(f"✓ Closed 50 Lugs in {close_time:.4f}s ({close_time/50*1000:.2f}ms per close)")
    print()
    
    # Measure file sizes
    print("[5/6] Measuring file sizes...")
    active_file = spoke_dir / 'lugs.jsonl'
    closed_file = spoke_dir / 'lugs-closed.jsonl'
    sessions_file = spoke_dir / 'lug-sessions.jsonl'
    
    active_size = active_file.stat().st_size if active_file.exists() else 0
    closed_size = closed_file.stat().st_size if closed_file.exists() else 0
    sessions_size = sessions_file.stat().st_size if sessions_file.exists() else 0
    
    print(f"  Active Lugs (lugs.jsonl):           {active_size:8,} bytes ({active_size/1024:.2f} KB)")
    print(f"  Closed Lugs (lugs-closed.jsonl):    {closed_size:8,} bytes ({closed_size/1024:.2f} KB)")
    print(f"  Sessions (lug-sessions.jsonl):      {sessions_size:8,} bytes ({sessions_size/1024:.2f} KB)")
    print(f"  TOTAL:                               {active_size+closed_size+sessions_size:8,} bytes ({(active_size+closed_size+sessions_size)/1024:.2f} KB)")
    print()
    
    # Measure load time
    print("[6/6] Measuring reload performance...")
    reload_times = []
    for i in range(5):
        reload_start = time.time()
        fresh_manager = LugManager(spoke_dir)
        reload_time = time.time() - reload_start
        reload_times.append(reload_time)
    
    avg_reload = sum(reload_times) / len(reload_times)
    print(f"✓ Average reload time: {avg_reload:.4f}s (across {len(reload_times)} iterations)")
    print()
    
    # Estimate context tokens
    print("Estimating context token usage...")
    
    # Read active file content
    active_content = ""
    if active_file.exists():
        with open(active_file, 'r') as f:
            active_content = f.read()
    
    active_tokens = estimate_tokens(active_content)
    print(f"  Active Lugs estimated tokens: ~{active_tokens:,}")
    print()
    
    # Generate results summary
    print("=" * 60)
    print("BENCHMARK RESULTS SUMMARY")
    print("=" * 60)
    print()
    print(f"Total Lugs Created:        100")
    print(f"Total Lugs Closed:         50")
    print(f"Active Lugs:               {len(manager.get_open_lugs())}")
    print(f"Dependencies Added:        10")
    print()
    print(f"Creation Time:             {create_time:.4f}s ({create_time/100*1000:.2f}ms per Lug)")
    print(f"Closure Time:              {close_time:.4f}s ({close_time/50*1000:.2f}ms per close)")
    print(f"Average Load Time:         {avg_reload:.4f}s")
    print()
    print(f"Active File Size:          {active_size:,} bytes ({active_size/1024:.2f} KB)")
    print(f"Closed File Size:          {closed_size:,} bytes ({closed_size/1024:.2f} KB)")
    print(f"Total Storage:             {active_size+closed_size:,} bytes ({(active_size+closed_size)/1024:.2f} KB)")
    print(f"Estimated Context Tokens:  ~{active_tokens:,}")
    print()
    
    # Return structured results
    return {
        'timestamp': datetime.now().isoformat(),
        'lugs_created': 100,
        'lugs_closed': 50,
        'active_lugs': len(manager.get_open_lugs()),
        'dependencies_added': 10,
        'timings': {
            'initialization_sec': round(init_time, 4),
            'creation_total_sec': round(create_time, 4),
            'creation_per_lug_ms': round(create_time/100*1000, 2),
            'closure_total_sec': round(close_time, 4),
            'closure_per_lug_ms': round(close_time/50*1000, 2),
            'avg_reload_sec': round(avg_reload, 4)
        },
        'file_sizes': {
            'active_bytes': active_size,
            'closed_bytes': closed_size,
            'total_bytes': active_size + closed_size,
            'active_kb': round(active_size/1024, 2),
            'closed_kb': round(closed_size/1024, 2),
            'total_kb': round((active_size+closed_size)/1024, 2)
        },
        'context_tokens': {
            'active_lugs_estimated': active_tokens
        }
    }


if __name__ == '__main__':
    # Use WAI-Spoke directory
    spoke_path = Path(__file__).parent.parent.parent / 'WAI-Spoke'
    
    if not spoke_path.exists():
        print(f"ERROR: Spoke directory not found at {spoke_path}")
        sys.exit(1)
    
    results = benchmark_lug_performance(spoke_path)
    
    # Save results to JSON
    results_file = spoke_path / 'benchmark-results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {results_file}")
