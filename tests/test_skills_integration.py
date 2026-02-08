import pytest
import json

SKILLS_FILE = "WAI-Spoke/WAI-Skills.jsonl"

def load_skills():
    skills = []
    with open(SKILLS_FILE) as f:
        for line in f:
            skills.append(json.loads(line))
    return skills

def test_complexity_advisor_exists():
    skills = load_skills()
    complexity = next((s for s in skills if s["id"] == "complexity_advisor"), None)
    assert complexity is not None
    assert complexity["lifecycle"] == "stable"

def test_stewardship_advisor_exists():
    skills = load_skills()
    stewardship = next((s for s in skills if s["id"] == "stewardship_advisor"), None)
    assert stewardship is not None
    assert "scope drift" in stewardship["description"].lower()

def test_signal_advisor_exists():
    skills = load_skills()
    signal = next((s for s in skills if s["id"] == "signal_advisor"), None)
    assert signal is not None
    assert signal["safety_level"] == "mutating"

def test_context_advisor_exists():
    skills = load_skills()
    context = next((s for s in skills if s["id"] == "context_advisor"), None)
    assert context is not None

def test_all_16_skills_exist():
    skills = load_skills()
    assert len(skills) == 16
    skill_ids = [s["id"] for s in skills]
    expected = [
        "wakeup", "status", "time", "rules", "closeout", "shipit",
        "teach", "learn", "red-light", "green-light",
        "complexity_advisor", "stewardship_advisor", "context_advisor",
        "foundation_advisor", "signal_advisor", "lug_advisor"
    ]
    for skill_id in expected:
        assert skill_id in skill_ids

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
