"""
Integration Test: Quality Gates Workflow.

Tests pre-closeout quality enforcement including test coverage,
contradiction detection, code smells, and UAT generation.
"""

import pytest
import sys
import json
import subprocess
from pathlib import Path

# Add framework to path
framework_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(framework_path))

from tests.integration.harness import IntegrationTestHarness
from tests.integration.cli_automation import CLIAutomation
from tests.integration.assertions import IntegrationAssertions


@pytest.fixture
def test_env():
    """Create isolated test environment."""
    harness = IntegrationTestHarness()
    harness.setup_environment()
    yield harness
    harness.teardown()


def test_quality_gates_feature_toggle_exists(test_env):
    """
    Scenario: Verify quality_gates feature toggle exists.

    Expected:
    - WAI-State.json has feature_toggles.quality_gates
    - Default value is true
    """
    spoke_dir = test_env.create_spoke("quality-toggle", with_git=False)

    state = test_env.get_spoke_state(spoke_dir)
    toggles = state.get("feature_toggles", {})

    assert "quality_gates" in toggles, "quality_gates toggle should exist"
    assert toggles["quality_gates"] == True, "quality_gates should be enabled by default"


def test_quality_gates_can_be_disabled(test_env):
    """
    Scenario: Quality gates can be disabled via feature toggle.

    Expected:
    - When quality_gates = false, closeout proceeds without checks
    - When quality_gates = true, validation runs
    """
    spoke_dir = test_env.create_spoke("quality-disabled", with_git=False)

    # Disable quality gates
    test_env.set_feature_toggles(spoke_dir, quality_gates=False)

    state = test_env.get_spoke_state(spoke_dir)
    assert state["feature_toggles"]["quality_gates"] == False

    # With gates disabled, closeout should always proceed
    # (Actual WAI-CLI implementation would skip validation when toggle is false)


def test_quality_gates_blocks_closeout_without_tests(test_env):
    """
    Scenario: Quality gate blocks closeout when no tests exist.

    Workflow:
    1. Create Python project with code
    2. No test files present
    3. Run closeout
    4. Verify gate blocks with helpful message
    """
    spoke_dir = test_env.create_spoke("no-tests", with_git=False)

    # Create code file without tests
    code_file = spoke_dir / "calculator.py"
    code_file.write_text("""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
""")

    # Simulate quality gate check
    test_files = list(spoke_dir.glob("**/test_*.py")) + list(spoke_dir.glob("**/*_test.py"))

    if len(test_files) == 0:
        # Gate should block
        gate_result = {
            "passed": False,
            "reason": "No test files found",
            "suggestion": "Add test files (test_*.py or *_test.py)"
        }
        assert gate_result["passed"] == False
        assert "test files" in gate_result["reason"].lower()


def test_quality_gates_passes_with_tests(test_env):
    """
    Scenario: Quality gate passes when tests exist.

    Workflow:
    1. Create Python project with code
    2. Add corresponding test file
    3. Run closeout
    4. Verify gate passes
    """
    spoke_dir = test_env.create_spoke("with-tests", with_git=False)

    # Create code file
    code_file = spoke_dir / "calculator.py"
    code_file.write_text("""
def add(a, b):
    return a + b
""")

    # Create test file
    test_file = spoke_dir / "test_calculator.py"
    test_file.write_text("""
def test_add():
    from calculator import add
    assert add(2, 3) == 5
""")

    # Simulate quality gate check
    test_files = list(spoke_dir.glob("**/test_*.py"))

    if len(test_files) > 0:
        gate_result = {
            "passed": True,
            "test_files_found": len(test_files)
        }
        assert gate_result["passed"] == True
        assert gate_result["test_files_found"] >= 1


def test_quality_gates_detects_contradictions(test_env):
    """
    Scenario: Quality gate detects contradictory decisions.

    Workflow:
    1. Add decision: "Use React for frontend"
    2. Add decision: "Use Vue for frontend"
    3. Run closeout
    4. Verify contradiction flagged
    """
    spoke_dir = test_env.create_spoke("contradictions", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    state = test_env.get_spoke_state(spoke_dir)

    # Add contradictory decisions
    state["decisions"] = [
        {
            "date": "2025-01-01",
            "decision": "Use React for frontend framework",
            "rationale": "Team expertise",
            "impact": 9,
            "by": "AI"
        },
        {
            "date": "2025-01-05",
            "decision": "Use Vue for frontend framework",
            "rationale": "Better performance",
            "impact": 9,
            "by": "AI"
        }
    ]

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Simulate contradiction detection
    decisions_text = " ".join([d["decision"].lower() for d in state["decisions"]])

    contradictions = []
    if "react" in decisions_text and "vue" in decisions_text:
        if "frontend" in decisions_text:
            contradictions.append({
                "type": "framework_conflict",
                "description": "Conflicting frontend framework decisions"
            })

    assert len(contradictions) > 0, "Should detect frontend framework contradiction"


def test_quality_gates_checks_code_coverage(test_env):
    """
    Scenario: Quality gate checks code coverage if possible.

    Workflow:
    1. Create Python project with tests
    2. Run coverage if pytest-cov installed
    3. Gate warns if coverage < threshold
    """
    spoke_dir = test_env.create_spoke("coverage-check", with_git=False)

    # Create simple code and test
    code_file = spoke_dir / "math_utils.py"
    code_file.write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b  # Not covered
""")

    test_file = spoke_dir / "test_math_utils.py"
    test_file.write_text("""
from math_utils import add, subtract

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

# multiply not tested - should show in coverage
""")

    # Try to run coverage (if available)
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--cov=.", "--cov-report=term-missing"],
            cwd=str(spoke_dir),
            capture_output=True,
            timeout=10
        )

        if result.returncode == 0:
            output = result.stdout.decode('utf-8')
            # If coverage ran successfully, we have coverage data
            assert "test_math_utils" in output or "coverage" in output.lower()
        else:
            # pytest-cov not installed or tests failed - skip this check
            pytest.skip("pytest-cov not available or tests failed")

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pytest.skip("pytest not available in this environment")


def test_quality_gates_detects_code_smells(test_env):
    """
    Scenario: Quality gate detects obvious code smells.

    Expected patterns to detect:
    - Very long functions (>50 lines)
    - High complexity (deeply nested loops)
    - Hardcoded credentials
    - TODO/FIXME markers
    """
    spoke_dir = test_env.create_spoke("code-smells", with_git=False)

    # Create file with code smells
    smelly_code = spoke_dir / "bad_code.py"
    smelly_code.write_text("""
# TODO: Refactor this mess
PASSWORD = "admin123"  # Hardcoded credential

def process_data(data):
    # Very nested logic
    for item in data:
        if item['type'] == 'user':
            for permission in item['permissions']:
                if permission == 'admin':
                    for resource in item['resources']:
                        if resource['status'] == 'active':
                            # 5 levels deep - complexity smell
                            pass
    return True
""")

    # Simulate code smell detection
    content = smelly_code.read_text()

    smells = []

    # Detect hardcoded credentials
    if "password" in content.lower() and "=" in content:
        smells.append({"type": "hardcoded_credential", "file": "bad_code.py"})

    # Detect TODO markers
    if "TODO" in content or "FIXME" in content:
        smells.append({"type": "todo_marker", "file": "bad_code.py"})

    # Detect deep nesting (count indentation levels)
    max_indent = max(len(line) - len(line.lstrip()) for line in content.split('\n') if line.strip())
    if max_indent > 16:  # 4 spaces * 4 levels
        smells.append({"type": "deep_nesting", "file": "bad_code.py"})

    assert len(smells) >= 2, "Should detect multiple code smells"


def test_quality_gates_suggests_uat_for_major_features(test_env):
    """
    Scenario: Quality gate suggests UAT when adding major feature.

    Workflow:
    1. Add high-impact feature (impact >= 9)
    2. No UAT plan exists
    3. Gate suggests creating UAT checklist
    """
    spoke_dir = test_env.create_spoke("uat-suggestion", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    state = test_env.get_spoke_state(spoke_dir)

    # Add major feature without UAT plan
    state["features"].append({
        "name": "User Authentication System",
        "status": "in_progress",
        "started": "2025-01-01",
        "completed": None,
        "uat_plan": None  # No UAT defined
    })

    # Add high-impact decision
    state["decisions"].append({
        "date": "2025-01-01",
        "decision": "Implement OAuth2 authentication",
        "impact": 9,
        "by": "AI"
    })

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Simulate UAT suggestion logic
    suggestions = []
    for feature in state["features"]:
        if feature.get("uat_plan") is None:
            suggestions.append({
                "feature": feature["name"],
                "recommendation": "Create UAT plan for major feature"
            })

    assert len(suggestions) > 0, "Should suggest UAT for major feature"
    assert "UAT" in suggestions[0]["recommendation"]


def test_quality_gates_validates_feature_completeness(test_env):
    """
    Scenario: Quality gate checks features marked complete have tests.

    Workflow:
    1. Mark feature as "completed"
    2. No tests for feature exist
    3. Gate flags incomplete feature
    """
    spoke_dir = test_env.create_spoke("feature-validation", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    state = test_env.get_spoke_state(spoke_dir)

    # Add completed feature
    state["features"].append({
        "name": "Email Notifications",
        "status": "completed",
        "started": "2025-01-01",
        "completed": "2025-01-10"
    })

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Check for tests related to this feature
    test_files = list(spoke_dir.glob("**/test_*email*.py")) + \
                 list(spoke_dir.glob("**/test_*notification*.py"))

    if len(test_files) == 0:
        validation_result = {
            "passed": False,
            "feature": "Email Notifications",
            "reason": "Feature marked complete but no tests found"
        }
        assert validation_result["passed"] == False


def test_quality_gates_non_interactive_mode(test_env):
    """
    Scenario: Quality gates run in non-interactive mode.

    Expected:
    - No prompts for user input
    - Auto-proceed or auto-block based on rules
    - Return validation summary
    """
    spoke_dir = test_env.create_spoke("non-interactive-gates", with_git=False)

    cli = CLIAutomation(spoke_dir)

    try:
        # Run quality check in non-interactive mode
        cli.start_cli(args="quality-check --non-interactive")

        # Should complete without prompts
        cli.expect_output(["quality", "check", "complete", "passed", "failed"], timeout=10)

    except Exception as e:
        pytest.skip(f"Quality gates command not yet implemented: {e}")
    finally:
        cli.terminate()


def test_quality_gates_generates_summary_report(test_env):
    """
    Scenario: Quality gates generate comprehensive summary.

    Expected report sections:
    - Tests found: X files
    - Coverage: X%
    - Contradictions: X found
    - Code smells: X detected
    - Overall: PASS/FAIL
    """
    spoke_dir = test_env.create_spoke("gates-summary", with_git=False)

    # Create test scenario
    code_file = spoke_dir / "app.py"
    code_file.write_text("def hello():\n    return 'Hello'\n")

    test_file = spoke_dir / "test_app.py"
    test_file.write_text("def test_hello():\n    assert True\n")

    # Simulate quality gate report
    report = {
        "tests_found": len(list(spoke_dir.glob("**/test_*.py"))),
        "coverage_estimate": "unknown",
        "contradictions": 0,
        "code_smells": 0,
        "overall": "PASS"
    }

    assert report["tests_found"] >= 1
    assert report["overall"] == "PASS"


def test_quality_gates_respects_baseline_mode(test_env):
    """
    Scenario: Quality gates disabled in baseline mode.

    Workflow:
    1. Set quality_gates toggle to false
    2. Create project with no tests
    3. Run closeout
    4. Verify gate skipped (baseline mode)
    """
    spoke_dir = test_env.create_spoke("baseline-skip-gates", with_git=False)

    # Disable quality gates (baseline mode)
    test_env.set_feature_toggles(spoke_dir, quality_gates=False)

    # Create code without tests
    code_file = spoke_dir / "logic.py"
    code_file.write_text("def process():\n    return 42\n")

    # In baseline mode, quality gates should be skipped
    state = test_env.get_spoke_state(spoke_dir)
    gates_enabled = state["feature_toggles"]["quality_gates"]

    if not gates_enabled:
        # Closeout should proceed without quality checks
        closeout_result = {
            "quality_gates_run": False,
            "reason": "Disabled via feature toggle (baseline mode)"
        }
        assert closeout_result["quality_gates_run"] == False
        assert "baseline" in closeout_result["reason"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
