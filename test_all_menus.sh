#!/bin/bash
# Comprehensive Menu Testing Script

echo "=========================================="
echo "WAI CLI Comprehensive Menu Test"
echo "=========================================="
echo ""

python3 -m pytest tests/integration/scenarios/test_menus.py -q
exit $?
