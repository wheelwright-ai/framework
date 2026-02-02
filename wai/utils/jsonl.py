"""
Streaming JSONL parsing utilities for memory-efficient file handling.
"""

import json
from pathlib import Path
from typing import Iterator, Dict, Any, Union


def stream_jsonl(file_path: Union[Path, str]) -> Iterator[Dict[str, Any]]:
    """
    Stream JSONL file line by line without loading all into memory.
    
    Args:
        file_path: Path to the JSONL file
        
    Yields:
        Parsed JSON objects from each line
        
    Example:
        for entry in stream_jsonl(Path("data.jsonl")):
            process(entry)
    """
    path = Path(file_path)
    if not path.exists():
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def stream_jsonl_tail(file_path: Union[Path, str], limit: int) -> Iterator[Dict[str, Any]]:
    """
    Stream the last N entries from a JSONL file.
    
    Uses a deque-style buffer to only keep the last N entries in memory.
    
    Args:
        file_path: Path to the JSONL file
        limit: Maximum number of entries to return
        
    Yields:
        Last N parsed JSON objects
    """
    from collections import deque
    
    path = Path(file_path)
    if not path.exists():
        return
    
    buffer = deque(maxlen=limit)
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                buffer.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    yield from buffer
