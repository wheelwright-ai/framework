import json
import os

SKILLS_FILE = "WAI-Spoke/WAI-Skills.jsonl"
COMMANDS_DIR = "templates/commands"
SPOKE_COMMANDS_DIR = "templates/WAI-Spoke/commands"

def load_skills():
    skills = []
    with open(SKILLS_FILE) as f:
        for line in f:
            skills.append(json.loads(line))
    return skills

def test_hub_has_16_skills():
    assert len(load_skills()) == 16

def test_spoke_has_16_skills():
    spoke = os.listdir(SPOKE_COMMANDS_DIR)
    assert len(spoke) == 16

def test_teach_cycle_complete():
    hub_skills = load_skills()
    spoke_files = os.listdir(SPOKE_COMMANDS_DIR)
    for skill in hub_skills:
        assert skill["file"] in spoke_files

def test_skill_ids_stable():
    skills = load_skills()
    ids = set(s["id"] for s in skills)
    assert "wakeup" in ids and "complexity_advisor" in ids

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
