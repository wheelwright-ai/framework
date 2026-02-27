#!/bin/bash
# Smoke Test for Hub Indexer (Map & Compass)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Testing Hub Indexer ==="

TEST_DIR=$(mktemp -d)
HUB_DIR="$TEST_DIR/Hub"
SPOKE_DIR="$TEST_DIR/Spoke"

echo "Test Dir: $TEST_DIR"

# 1. Create Hub
echo "Creating Hub..."
mkdir -p "$HUB_DIR/registry"
echo '{"version":"2.0", "projects":[]}' > "$HUB_DIR/registry/wheel-projects.json"
echo '{"version":"2.0"}' > "$HUB_DIR/hub-profile.json"

# 2. Create Spoke
echo "Creating Spoke..."
mkdir -p "$SPOKE_DIR"
../../WAI init "$SPOKE_DIR" > /dev/null

# Configure Spoke to point to Hub
STATE_FILE="$SPOKE_DIR/WAI-Spoke/WAI-State.json"
jq --arg hub "$HUB_DIR" '.wheel.hub_path = $hub' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

# 3. Add High Impact Signal
echo "Adding Signal..."
SIGNAL='{"id":"sig-1", "impact":9, "confidence":0.9, "content":"Use dependency injection", "context":{"problem":"Coupling"}, "timestamp":"2023-01-01T00:00:00Z"}'
echo "$SIGNAL" >> "$SPOKE_DIR/WAI-Spoke/WAI-Signals.jsonl"

# 4. Run WAI teach
echo "Running WAI teach..."
../../WAI teach "$SPOKE_DIR"

# 5. Verify Hub Index exists
if [[ -f "$HUB_DIR/WAI-Hub-Index.md" ]]; then
    echo "✓ Hub Index generated"
else
    echo "✗ Hub Index MISSING"
    exit 1
fi

# 6. Verify Spoke Reference Map exists
if [[ -f "$SPOKE_DIR/WAI-Spoke/reference/WAI-Hub-Index.md" ]]; then
    echo "✓ Map delivered to Spoke"
else
    echo "✗ Map delivery FAILED"
    exit 1
fi

# 7. Verify Index Content (basic)
CONTENT=$(cat "$HUB_DIR/WAI-Hub-Index.md")
if [[ "$CONTENT" == *"# 🗺️ Wheelwright Hub Index"* ]]; then
    echo "✓ Index content valid"
else
    echo "✗ Index content invalid"
    echo "$CONTENT"
    exit 1
fi

echo "=== Hub Indexer Tests Passed ==="
rm -rf "$TEST_DIR"
