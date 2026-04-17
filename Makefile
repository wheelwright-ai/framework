# Wheelwright Framework - Test & Quality Gates
# Used by wai-closeout quality gates (Step 0b)

.PHONY: test test-all test-unit test-integration test-e2e test-behavioral test-health clean

# Default: Run the stable public integration suite
test:
	@echo "Running public integration suite..."
	@./run-integration-tests.sh --mode=all --json=results.json

# Run all test categories
test-all: test-e2e test-behavioral test-health
	@echo "All test suites passed"

# Public integration suite
test-e2e:
	@echo "Running public integration suite..."
	@./run-integration-tests.sh --mode=all --json=results.json

# Behavioral tests (real file operations, no mocks)
test-behavioral:
	@echo "Running behavioral tests..."
	@python3 -m pytest tests/behavioral/ -v

# Spoke health check (validates framework spoke against own rules)
test-health:
	@echo "Running spoke health check..."
	@python3 tools/spoke_health_check.py . --quick

# Integration tests (baseline comparison, performance)
test-integration:
	@echo "Running integration tests..."
	@./run-integration-tests.sh --mode=all --json=results.json

# Unit tests (when we have them)
test-unit:
	@echo "No unit tests defined yet"

# Clean test artifacts
clean:
	@rm -f results.json baseline-results.json report.txt
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Test artifacts cleaned"
