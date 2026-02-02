"""
Integration tests for Lug performance benchmarks.

Tests 100-Lug scenarios for:
- Creation time
- File size
- Load time
- Query performance
- Token estimation
"""

import pytest
import json
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wai.lugs import LugManager


@pytest.fixture
def temp_spoke_dir():
    """Create temporary spoke directory for performance tests."""
    temp_dir = Path(tempfile.mkdtemp())
    wai_spoke = temp_dir / 'WAI-Spoke'
    wai_spoke.mkdir()
    
    # Create minimal WAI-State.json
    state = {
        "project_metadata": {"name": "Perf Test Project"},
        "_session_state": {
            "current_session": {
                "session_id": "perf-session-001",
                "started_at": datetime.now().isoformat()
            }
        }
    }
    (wai_spoke / 'WAI-State.json').write_text(json.dumps(state))
    
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_100_lugs_creation_time(temp_spoke_dir):
    """Measure time to create 100 Lugs."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    start_time = time.time()
    
    for i in range(100):
        manager.create_lug(
            title=f"Performance Test Lug {i}",
            lug_type=["work", "bug", "issue", "epic"][i % 4],
            priority=["low", "medium", "high"][i % 3],
            impact=["small", "medium", "large"][i % 3],
            value=i % 10,
            justification=f"Test justification for lug {i}"
        )
    
    elapsed = time.time() - start_time
    
    # Should complete in reasonable time (<5 seconds)
    assert elapsed < 5.0, f"Creation took {elapsed:.2f}s, expected <5s"
    
    # Verify all created
    assert len(manager.lugs) == 100
    
    print(f"\\n✓  Created 100 Lugs in {elapsed:.3f}s ({elapsed/100*1000:.1f}ms per Lug)")


def test_100_lugs_file_size(temp_spoke_dir):
    """Measure lugs.jsonl file size with 100 Lugs."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # Create 100 Lugs
    for i in range(100):
        manager.create_lug(
            title=f"File Size Test Lug {i}",
            lug_type="work",
            priority="medium",
            impact="medium",
            value=5
        )
    
    lugs_file = temp_spoke_dir / 'WAI-Spoke' / 'lugs.jsonl'
    file_size = lugs_file.stat().st_size
    
    # Should be < 50KB (minification should help)
    assert file_size < 50000, f"File size {file_size} bytes, expected <50KB"
    
    avg_size_per_lug = file_size / 100
    print(f"\\n✓  100 Lugs file size: {file_size:,} bytes ({file_size/1024:.1f}KB)")
    print(f"   Average per Lug: {avg_size_per_lug:.0f} bytes")


def test_100_lugs_load_time(temp_spoke_dir):
    """Measure LugManager initialization time with 100 Lugs."""
    # First create 100 Lugs
    manager1 = LugManager(temp_spoke_dir / 'WAI-Spoke')
    for i in range(100):
        manager1.create_lug(title=f"Load Test Lug {i}")
    
    # Now benchmark loading
    start_time = time.time()
    manager2 = LugManager(temp_spoke_dir / 'WAI-Spoke')
    elapsed = time.time() - start_time
    
    # Should load quickly (<0.5 seconds)
    assert elapsed < 0.5, f"Load took {elapsed:.2f}s, expected <0.5s"
    assert len(manager2.lugs) == 100
    
    print(f"\\n✓  Loaded 100 Lugs in {elapsed:.3f}s")


def test_100_lugs_query_time(temp_spoke_dir):
    """Measure query time (list_lugs, get_lug by prefix)."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # Create 100 varied Lugs
    lug_ids = []
    for i in range(100):
        lug = manager.create_lug(
            title=f"Query Test Lug {i}",
            lug_type=["work", "bug", "issue"][i % 3],
            status=["open", "in_progress", "blocked"][i % 3],
            priority=["low", "medium", "high"][i % 3]
        )
        lug_ids.append(lug.id)
    
    # Benchmark list_lugs queries
    start = time.time()
    all_lugs = manager.list_lugs()
    list_all_time = time.time() - start
    
    start = time.time()
    bugs = manager.list_lugs(lug_type="bug")
    list_type_time = time.time() - start
    
    start = time.time()
    high_pri = manager.list_lugs(priority="high")
    list_priority_time = time.time() - start
    
    # Benchmark get_lug by prefix
    start = time.time()
    for lug_id in lug_ids[:10]:  # Test 10 lookups
        manager.get_lug(lug_id[:4])
    get_time = time.time() - start
    
    # All queries should be fast (<0.1s or 100ms)
    assert list_all_time < 0.1, f"list_lugs() took {list_all_time:.3f}s"
    assert list_type_time < 0.1, f"list_lugs(type) took {list_type_time:.3f}s"
    assert list_priority_time < 0.1, f"list_lugs(priority) took {list_priority_time:.3f}s"
    assert get_time < 0.1, f"get_lug() 10x took {get_time:.3f}s"
    
    print(f"\\n✓  Query performance (100 Lugs):")
    print(f"   list_lugs():           {list_all_time*1000:.1f}ms")
    print(f"   list_lugs(type=...):   {list_type_time*1000:.1f}ms")
    print(f"   list_lugs(priority=...): {list_priority_time*1000:.1f}ms")
    print(f"   get_lug() 10x:         {get_time*1000:.1f}ms ({get_time/10*1000:.1f}ms each)")


def test_100_lugs_tokens_estimate(temp_spoke_dir):
    """Estimate total tokens for 100 Lugs in context."""
    manager = LugManager(temp_spoke_dir / 'WAI-Spoke')
    
    # Create 100 realistic Lugs
    for i in range(100):
        manager.create_lug(
            title=f"Task {i}: Implement module {i//10 + 1}",
            lug_type="work",
            priority="medium",
            impact="medium",
            value=5,
            justification=f"Required for milestone {i//20 + 1}. Dependencies on prior modules."
        )
    
    # Get all Lugs
    lugs = manager.list_lugs()
    assert len(lugs) == 100
    
    # Serialize to JSON (simulates WAI-Point context)
    json_full = json.dumps([l.to_dict() for l in lugs], indent=2)
    json_compact = json.dumps([l.to_dict() for l in lugs])
    
    # Rough token estimation (~4 chars per token for typical text)
    tokens_full = len(json_full) / 4
    tokens_compact = len(json_compact) / 4
    
    # Should be reasonable (<15k tokens for compact, <20k for full)
    assert tokens_compact < 15000, f"Compact JSON: {tokens_compact:.0f} tokens, expected <15k"
    assert tokens_full < 20000, f"Full JSON: {tokens_full:.0f} tokens, expected <20k"
    
    lugs_file = temp_spoke_dir / 'WAI-Spoke' / 'lugs.jsonl'
    file_size = lugs_file.stat().st_size
    
    print(f"\\n✓  Token estimation (100 Lugs):")
    print(f"   Compact JSON: {tokens_compact:,.0f} tokens (~{len(json_compact):,} chars)")
    print(f"   Pretty JSON:  {tokens_full:,.0f} tokens (~{len(json_full):,} chars)")
    print(f"   JSONL file:   {file_size:,} bytes ({file_size/1024:.1f}KB)")
    print(f"   Per Lug avg:  {tokens_compact/100:.0f} tokens")
