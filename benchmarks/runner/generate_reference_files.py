#!/usr/bin/env python3
"""
Generate fake reference files for benchmarking.
Creates compressible repetitive content to simulate documentation.
"""
import os
import sys
from pathlib import Path

def generate_fake_docs(target_dir: Path, size_mb: int):
    """
    Generate fake documentation files totaling approximately size_mb.
    Uses repetitive lorem ipsum for good compression ratio.
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    # Lorem ipsum base text (compresses well when repeated)
    lorem_base = """
# API Reference Documentation

## Overview
This is automatically generated reference documentation for the API.
It contains detailed information about all endpoints, parameters, and responses.

## Authentication
All API requests require authentication using a Bearer token.

### Example Request
```
GET /api/v1/resource
Authorization: Bearer <token>
```

## Endpoints

### GET /api/v1/users
Returns a list of users.

**Parameters:**
- page (integer): Page number for pagination
- limit (integer): Number of items per page
- sort (string): Sort field

**Response:**
```json
{
  "users": [],
  "total": 0,
  "page": 1
}
```

### POST /api/v1/users
Creates a new user.

**Body:**
```json
{
  "name": "string",
  "email": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "email": "string"
}
```

## Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

"""

    # Calculate how many times to repeat
    base_size = len(lorem_base.encode('utf-8'))
    target_bytes = size_mb * 1024 * 1024
    num_files = 10  # Spread across multiple files
    bytes_per_file = target_bytes // num_files
    repeats_per_file = bytes_per_file // base_size

    print(f"Generating {size_mb}MB of reference files in {target_dir}")
    print(f"  Files: {num_files}")
    print(f"  ~{bytes_per_file / (1024*1024):.1f}MB per file")

    for i in range(num_files):
        filepath = target_dir / f"api_reference_v{i+1}.md"
        with open(filepath, 'w') as f:
            f.write(f"# API Reference Volume {i+1}\n\n")
            for _ in range(repeats_per_file):
                f.write(lorem_base)

        actual_size = filepath.stat().st_size
        print(f"  ✓ {filepath.name}: {actual_size / (1024*1024):.2f}MB")

    total_size = sum(f.stat().st_size for f in target_dir.glob("*.md"))
    print(f"✅ Total generated: {total_size / (1024*1024):.2f}MB")
    return total_size

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_reference_files.py <target_dir> <size_mb>")
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    size_mb = int(sys.argv[2])

    generate_fake_docs(target_dir, size_mb)
