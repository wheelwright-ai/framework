import os

EXAMPLES_FILE = "templates/commands/SKILL-EXAMPLES.md"
COMMANDS_DIR = "templates/commands"

def test_skill_examples_exists():
    assert os.path.exists(EXAMPLES_FILE)

def test_skill_files_exist():
    expected_skills = [
        "wai.md", "wai-status.md", "wai-time.md", "wai-rules.md",
        "wai-closeout.md", "wai-shipit.md", "wai-teach.md", "wai-learn.md",
        "wai-red-light.md", "wai-green-light.md",
        "wai-complexity-advisor.md", "wai-stewardship-advisor.md",
        "wai-context-advisor.md", "wai-foundation-advisor.md",
        "wai-signal-advisor.md", "wai-lug-advisor.md"
    ]
    for skill_file in expected_skills:
        path = os.path.join(COMMANDS_DIR, skill_file)
        assert os.path.exists(path), f"Missing: {skill_file}"

def test_skill_files_have_content():
    expected_skills = [
        "wai.md", "wai-status.md", "wai-time.md", "wai-rules.md",
        "wai-closeout.md", "wai-shipit.md", "wai-teach.md", "wai-learn.md",
        "wai-red-light.md", "wai-green-light.md",
        "wai-complexity-advisor.md", "wai-stewardship-advisor.md",
        "wai-context-advisor.md", "wai-foundation-advisor.md",
        "wai-signal-advisor.md", "wai-lug-advisor.md"
    ]
    for skill_file in expected_skills:
        path = os.path.join(COMMANDS_DIR, skill_file)
        with open(path) as f:
            content = f.read()
            assert len(content) > 100, f"{skill_file} too short"
            assert "#" in content, f"{skill_file} missing header"

def test_examples_file_has_all_skills():
    with open(EXAMPLES_FILE) as f:
        content = f.read()
    skill_names = [
        "wai", "status", "time", "rules", "closeout", "shipit",
        "teach", "learn", "red-light", "green-light",
        "Complexity Advisor", "Stewardship Advisor", "Context Advisor",
        "Foundation Advisor", "Signal Advisor", "Lug Advisor"
    ]
    for skill_name in skill_names:
        assert skill_name in content, f"{skill_name} not in SKILL-EXAMPLES.md"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
