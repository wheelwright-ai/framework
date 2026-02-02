#!/usr/bin/env python3
"""Epic-008 Lug Performance Benchmark - Run from framework root."""

import json
import time
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from wai.lugs import LugManager


def estimate_tokens(text: str) -> int:
    """Approximate token count (4 chars ≈ 1 token)."""
    return len(text) // 4


def create_sample_lug_data(idx: int, closed: bool = False):
    """Create realistic sample Lug data."""
    return {
        'id': f'epic008-lug-{idx:05d}',
        'title': f'Task {idx}: Implement feature component {idx}',
        'type': 'work' if idx % 3 != 0 else 'bug',
        'status': 'closed' if closed else 'open',
        'priority': ['low', 'medium', 'high'][idx % 3],
        'impact': ['small', 'medium', 'large'][idx % 3],
        'value': (idx % 10) + 1,
        'session_id': f'session-{idx // 10}',
        'deps': [f'epic008-lug-{max(0, idx-1):05d}'] if idx > 0 and idx % 5 == 0 else [],
        'justification': f'Required for epic-008 validation scenario {idx}',
        'from_file': f'src/module_{idx % 10}.py' if idx % 2 == 0 else None,
        'extras': {'benchmark': True, 'batch': idx // 20}
    }


print("\n" + "="*80)
print("  EPIC-008 LUG PERFORMANCE BENCHMARK")
print("="*80 + "\n")

# Create temporary spoke directory
temp_dir = Path(tempfile.mkdtemp(prefix='epic008_benchmark_'))
print(f"📁 Temporary spoke: {temp_dir}\n")

try:
    # Initialize LugManager
    print("⏳ Initializing LugManager...")
    manager = LugManager(temp_dir)
    
    # Create 100 Lugs (50 open, 50 closed)
    total_lugs = 100
    closed_count = 50
    
    print(f"⏳ Creating {total_lugs} Lugs ({closed_count} closed, {total_lugs - closed_count} open)...\n")
    
    creation_start = time.perf_counter()
    
    for i in range(total_lugs):
        is_closed = i < closed_count
        lug_data = create_sample_lug_data(i, closed=is_closed)
        
        # Create Lug
        lug = manager.create_lug(
            title=lug_data['title'],
            lug_type=lug_data['type'],
            priority=lug_data['priority'],
            impact=lug_data['impact'],
            value=lug_data['value'],
            session_id=lug_data['session_id'],
            deps=lug_data['deps'],
            justification=lug_data['justification'],
            origin=None,
            from_file=lug_data['from_file'],
            extras=lug_data['extras']
        )
        
        # Close if needed
        if is_closed:
            manager.close_lug(
                lug.id,
                summary=f'Completed task {i} with full implementation',
                skip_policy_check=True
            )
        
        if (i + 1) % 20 == 0:
            print(f"  ✓ Created {i + 1}/{total_lugs} Lugs...")
    
    creation_time = (time.perf_counter() - creation_start) * 1000
    print(f"\n✅ Creation complete: {creation_time:.2f}ms\n")
    
    # File Size Metrics
    lugs_file = temp_dir / 'lugs.jsonl'
    closed_file = temp_dir / 'lugs-closed.jsonl'
    sessions_file = temp_dir / 'lug-sessions.jsonl'
    
    lugs_size = lugs_file.stat().st_size if lugs_file.exists() else 0
    closed_size = closed_file.stat().st_size if closed_file.exists() else 0
    sessions_size = sessions_file.stat().st_size if sessions_file.exists() else 0
    total_size = lugs_size + closed_size + sessions_size
    
    # Load Time Metrics
    print("⏳ Measuring load time...")
    load_start = time.perf_counter()
    fresh_manager = LugManager(temp_dir)
    load_time = (time.perf_counter() - load_start) * 1000
    
    # Query Performance
    print("⏳ Measuring query performance...")
    query_start = time.perf_counter()
    open_lugs = fresh_manager.get_open_lugs()
    query_time = (time.perf_counter() - query_start) * 1000
    
    closed_query_start = time.perf_counter()
    closed_lugs = fresh_manager.get_closed_lugs()
    closed_query_time = (time.perf_counter() - closed_query_start) * 1000
    
    # Token Estimate
    print("⏳ Estimating token counts...\n")
    active_content = ""
    for lug in open_lugs:
        active_content += json.dumps(lug.to_dict()) + "\n"
    active_tokens = estimate_tokens(active_content)
    
    full_content = active_content
    for lug in closed_lugs:
        full_content += json.dumps(lug.to_dict()) + "\n"
    full_tokens = estimate_tokens(full_content)
    
    token_savings = ((full_tokens - active_tokens) / full_tokens * 100) if full_tokens > 0 else 0
    
    # Results
    results = {
        'timestamp': datetime.now().isoformat(),
        'scenario': {
            'total_lugs': total_lugs,
            'open_lugs': len(open_lugs),
            'closed_lugs': len(closed_lugs)
        },
        'file_sizes': {
            'lugs_active_kb': round(lugs_size / 1024, 2),
            'lugs_closed_kb': round(closed_size / 1024, 2),
            'total_kb': round(total_size / 1024, 2)
        },
        'performance': {
            'load_time_ms': round(load_time, 2),
            'query_open_time_ms': round(query_time, 4),
            'query_closed_time_ms': round(closed_query_time, 4)
        },
        'token_estimates': {
            'active_tokens': active_tokens,
            'full_tokens': full_tokens,
            'token_savings_percent': round(token_savings, 2)
        }
    }
    
    print("\n" + "="*80)
    print("  RESULTS")
    print("="*80)
    
    print(f"\n📊 File Sizes:")
    print(f"   Active Lugs:  {results['file_sizes']['lugs_active_kb']:>8.2f} KB")
    print(f"   Closed Lugs:  {results['file_sizes']['lugs_closed_kb']:>8.2f} KB")
    print(f"   Total:        {results['file_sizes']['total_kb']:>8.2f} KB")
    
    print(f"\n⚡ Performance:")
    print(f"   Load Time:    {results['performance']['load_time_ms']:>8.2f} ms")
    print(f"   Query Open:   {results['performance']['query_open_time_ms']:>8.4f} ms")
    print(f"   Query Closed: {results['performance']['query_closed_time_ms']:>8.4f} ms")
    
    print(f"\n🎯 Token Estimates:")
    print(f"   Active:       {results['token_estimates']['active_tokens']:>8,} tokens")
    print(f"   Full:         {results['token_estimates']['full_tokens']:>8,} tokens")
    print(f"   Savings:      {results['token_estimates']['token_savings_percent']:>8.2f}%")
    
    # Save results
    with open('benchmark_epic008.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Results saved to: benchmark_epic008.json")
    print("\n✅ Benchmark complete!\n")

finally:
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
