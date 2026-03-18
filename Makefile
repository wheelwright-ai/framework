# Wheelwright Framework - Test & Quality Gates
# Used by wai-shipit quality gates (Step 5a)

.PHONY: test test-all test-unit test-integration test-e2e clean

# Default: Run all E2E tests (matches shipit expectations)
test:
	@echo "Running E2E skill behavior tests..."
	@python3 benchmarks/e2e/test_skills.py

# Run all test categories
test-all: test-e2e test-integration
	@echo "✅ All test suites passed"

# E2E behavioral tests (skill system validation)
test-e2e:
	@echo "Running E2E behavioral tests..."
	@python3 benchmarks/e2e/test_skills.py

# Integration tests (baseline comparison, performance)
test-integration:
	@echo "Running integration tests..."
	@./run-integration-tests.sh --mode=all --json=results.json

# Unit tests (when we have them)
test-unit:
	@echo "⚠️  No unit tests defined yet"

# Clean test artifacts
clean:
	@rm -f results.json baseline-results.json report.txt
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Test artifacts cleaned"
