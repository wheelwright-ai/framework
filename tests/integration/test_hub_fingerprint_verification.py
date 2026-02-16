import pytest
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

from wai.hub import HubManager
from wai.commands.teach import distribute_teach_command
from wai.teach_reconciliation import perform_teaching_adoption, scan_teach_ingest_dir
from wai.upgrade_adoption import UpgradeAdoptionPlanBuilder

# --- Helper functions for test setup ---
def create_dummy_hub(tmp_path: Path, hub_name="test_hub") -> Path:
    """Creates a dummy hub with a generated fingerprint."""
    hub_path = tmp_path / hub_name
    hub_path.mkdir()
    (hub_path / 'registry').mkdir()
    (hub_path / 'learnings').mkdir()
    (hub_path / '.WAI-registry').mkdir()

    wai_spoke_dir = hub_path / 'WAI-Spoke'
    wai_spoke_dir.mkdir()
    (wai_spoke_dir / 'seed' / 'ingest').mkdir(parents=True)
    (wai_spoke_dir / 'seed' / 'reference').mkdir(parents=True)
    (wai_spoke_dir / 'reference').mkdir(parents=True)
    (wai_spoke_dir / '_framework').mkdir(parents=True)

    hub_profile_path = hub_path / 'hub-profile.json'
    profile_data = {
        "hub_config": {}
    }
    hub_profile_path.write_text(json.dumps(profile_data, indent=2))

    # Use HubManager's _create_hub_structure to ensure fingerprint generation
    hub_manager = HubManager()
    with patch('wai.hub.print_warning'): # Suppress print_warning during test hub creation
        hub_manager._create_hub_structure(hub_path)
    
    return hub_path

def create_dummy_spoke(tmp_path: Path, spoke_name="test_spoke") -> Path:
    """Creates a dummy spoke with WAI-Spoke structure."""
    spoke_path = tmp_path / spoke_name
    spoke_path.mkdir()
    wai_spoke_dir = spoke_path / 'WAI-Spoke'
    wai_spoke_dir.mkdir()
    (wai_spoke_dir / 'seed' / 'ingest').mkdir(parents=True)
    
    # Create a dummy WAI-State.json for the spoke
    wai_state_data = {
        "_spoke_id": spoke_name,
        "_hub_profile": {
            "hub_config": {
                "hub_path": "" # Will be filled later
            }
        },
        "wheelwright": {
            "version": "3.0.0",
            "structure_version": "3.0"
        }
    }
    (wai_spoke_dir / 'WAI-State.json').write_text(json.dumps(wai_state_data, indent=2))
    return spoke_path

def setup_framework_templates(tmp_path: Path, framework_version="3.1.0") -> Path:
    """Sets up minimal framework templates for teaching."""
    framework_path = tmp_path / "framework"
    framework_path.mkdir()
    templates_path = framework_path / "templates"
    (templates_path / "WAI-Spoke").mkdir(parents=True)
    (templates_path / "HUB").mkdir(parents=True)

    # Dummy WAI-Guide.md for spoke
    (templates_path / "WAI-Spoke" / "WAI-Guide.md").write_text("Spoke Guide Content")
    
    # Dummy WAI-State.json for hub (if teaching a hub)
    hub_wai_spoke_templates_dir = templates_path / "HUB" / "WAI-Spoke"
    hub_wai_spoke_templates_dir.mkdir(parents=True)
    (hub_wai_spoke_templates_dir / "WAI-State.json").write_text(json.dumps({
        "wheelwright": {"is_hub": True},
        "_hub_profile": {"hub_config": {"fingerprint": None}} # Placeholder for fingerprint
    }, indent=2))

    # Mock FRAMEWORK_VERSION
    with patch('wai.commands.teach.FRAMEWORK_VERSION', framework_version):
        return framework_path

@pytest.fixture
def test_setup(tmp_path):
    """Provides a setup for hub, spoke, and framework paths."""
    framework_path = setup_framework_templates(tmp_path)
    hub_path = create_dummy_hub(tmp_path, "my_hub")
    spoke_path = create_dummy_spoke(tmp_path, "my_spoke")
    
    return {
        "framework_path": framework_path,
        "hub_path": hub_path,
        "spoke_path": spoke_path
    }

# --- Tests ---

def test_hub_fingerprint_generation(test_setup):
    """Ensures a unique fingerprint is generated for a new hub."""
    hub_path = test_setup["hub_path"]
    
    hub_manager = HubManager()
    fingerprint = hub_manager.get_hub_fingerprint(hub_path)
    
    assert fingerprint is not None
    assert isinstance(fingerprint, str)
    assert len(fingerprint) > 10 # Basic check for UUID-like string

def test_hub_fingerprint_retrieval(test_setup):
    """Ensures get_hub_fingerprint correctly retrieves an existing fingerprint."""
    hub_path = test_setup["hub_path"]
    
    # Manually set a known fingerprint
    known_fingerprint = "test-123-abc"
    hub_profile_path = hub_path / 'hub-profile.json'
    profile_data = json.loads(hub_profile_path.read_text())
    profile_data['hub_config']['fingerprint'] = known_fingerprint
    hub_profile_path.write_text(json.dumps(profile_data, indent=2))
    
    hub_manager = HubManager()
    retrieved_fingerprint = hub_manager.get_hub_fingerprint(hub_path)
    
    assert retrieved_fingerprint == known_fingerprint

def test_hub_fingerprint_no_profile_file(tmp_path):
    """Ensures get_hub_fingerprint returns None if hub-profile.json is missing."""
    hub_path = tmp_path / "no_profile_hub"
    hub_path.mkdir()
    hub_manager = HubManager()
    fingerprint = hub_manager.get_hub_fingerprint(hub_path)
    assert fingerprint is None

def test_hub_fingerprint_malformed_profile(tmp_path):
    """Ensures get_hub_fingerprint returns None if hub-profile.json is malformed."""
    hub_path = tmp_path / "malformed_profile_hub"
    hub_path.mkdir()
    (hub_path / 'hub-profile.json').write_text("{malformed json")
    hub_manager = HubManager()
    fingerprint = hub_manager.get_hub_fingerprint(hub_path)
    assert fingerprint is None

@patch('wai.commands.teach.print_success')
@patch('wai.commands.teach.print_info')
@patch('wai.commands.teach.print_error')
@patch('wai.commands.teach.print_warning')
@patch('wai.commands.teach.get_logger')
def test_distribute_teach_command_signs_plan_with_fingerprint(
    mock_get_logger, mock_print_warning, mock_print_error, mock_print_info, mock_print_success,
    test_setup):
    """
    Ensures distribute_teach_command signs the upgrade plan with the hub's fingerprint
    when a hub_path is provided.
    """
    framework_path = test_setup["framework_path"]
    hub_path = test_setup["hub_path"]
    spoke_path = test_setup["spoke_path"]

    # Configure spoke to know about the hub
    spoke_wai_state_path = spoke_path / "WAI-Spoke" / "WAI-State.json"
    spoke_state_data = json.loads(spoke_wai_state_path.read_text())
    spoke_state_data['_hub_profile']['hub_config']['hub_path'] = str(hub_path)
    spoke_wai_state_path.write_text(json.dumps(spoke_state_data, indent=2))

    # Get the expected hub fingerprint
    hub_manager = HubManager()
    expected_fingerprint = hub_manager.get_hub_fingerprint(hub_path)
    assert expected_fingerprint is not None

    # Run distribute command
    success = distribute_teach_command(spoke_path, hub_path, framework_path)
    assert success

    # Verify the generated plan in spoke's ingest directory
    plan_path = spoke_path / 'upgrade-adoption-plan.json'
    assert plan_path.exists()
    plan_data = json.loads(plan_path.read_text())

    assert 'verification' in plan_data
    assert 'hub_fingerprint' in plan_data['verification']
    assert plan_data['verification']['hub_fingerprint'] == expected_fingerprint

@patch('wai.commands.teach.print_success')
@patch('wai.commands.teach.print_info')
@patch('wai.commands.teach.print_error')
@patch('wai.commands.teach.print_warning')
@patch('wai.commands.teach.get_logger')
def test_distribute_teach_command_no_signing_without_hub_path(
    mock_get_logger, mock_print_warning, mock_print_error, mock_print_info, mock_print_success,
    test_setup):
    """
    Ensures distribute_teach_command does not sign the plan when no hub_path is provided.
    """
    framework_path = test_setup["framework_path"]
    spoke_path = test_setup["spoke_path"]

    # Run distribute command without hub_path
    success = distribute_teach_command(spoke_path, None, framework_path)
    assert success

    # Verify the generated plan in spoke's ingest directory
    plan_path = spoke_path / 'upgrade-adoption-plan.json'
    assert plan_path.exists()
    plan_data = json.loads(plan_path.read_text())

    assert 'verification' not in plan_data or 'hub_fingerprint' not in plan_data['verification']

@patch('wai.utils.input.print_success')
@patch('wai.utils.input.print_info')
@patch('wai.utils.input.print_error')
@patch('wai.utils.input.print_warning')
def test_perform_teaching_adoption_matching_fingerprints(
    mock_print_warning, mock_print_error, mock_print_info, mock_print_success,
    test_setup):
    """
    Ensures perform_teaching_adoption succeeds when plan fingerprint matches configured spoke fingerprint.
    """
    framework_path = test_setup["framework_path"]
    hub_path = test_setup["hub_path"]
    spoke_path = test_setup["spoke_path"]

    # 1. Configure spoke with hub's fingerprint
    hub_manager = HubManager()
    expected_fingerprint = hub_manager.get_hub_fingerprint(hub_path)
    spoke_wai_state_path = spoke_path / "WAI-Spoke" / "WAI-State.json"
    spoke_state_data = json.loads(spoke_wai_state_path.read_text())
    spoke_state_data['_hub_profile']['hub_config']['hub_path'] = str(hub_path) # Needs actual path for get_hub_fingerprint
    spoke_wai_state_path.write_text(json.dumps(spoke_state_data, indent=2))

    # 2. Distribute a signed plan to the spoke
    distribute_teach_command(spoke_path, hub_path, framework_path)
    
    # 3. Create a teaching entry for the plan
    ingest_dir = spoke_path / "WAI-Spoke" / "seed" / "ingest"
    (ingest_dir / "manifest.json").write_text(json.dumps({"plan_teaching": {
        "path": "upgrade-adoption-plan.json",
        "safe_to_auto_adopt": True,
        "verification": {"hub_fingerprint": expected_fingerprint} # Add verification info
    }}, indent=2))
    
    # Copy the plan into ingest as a teaching file
    shutil.copy2(spoke_path / 'upgrade-adoption-plan.json', ingest_dir / "plan_teaching.teaching")

    # 4. Perform adoption
    teaching_entry = {
        "id": "plan_teaching",
        "file_path": str(ingest_dir / "plan_teaching.teaching"),
        "metadata": {
            "path": "upgrade-adoption-plan.json",
            "safe_to_auto_adopt": True,
            "verification": {"hub_fingerprint": expected_fingerprint}
        }
    }
    
    result = perform_teaching_adoption(spoke_path, teaching_entry)
    assert result is True
    mock_print_error.assert_not_called()
    mock_print_warning.assert_not_called()

@patch('wai.utils.input.print_success')
@patch('wai.utils.input.print_info')
@patch('wai.utils.input.print_error')
@patch('wai.utils.input.print_warning')
def test_perform_teaching_adoption_mismatching_fingerprints(
    mock_print_warning, mock_print_error, mock_print_info, mock_print_success,
    test_setup):
    """
    Ensures perform_teaching_adoption refuses when plan fingerprint mismatches.
    """
    framework_path = test_setup["framework_path"]
    hub_path = test_setup["hub_path"]
    spoke_path = test_setup["spoke_path"]

    # 1. Configure spoke with a FAKE hub's fingerprint
    fake_fingerprint = "fake-fingerprint-123"
    spoke_wai_state_path = spoke_path / "WAI-Spoke" / "WAI-State.json"
    spoke_state_data = json.loads(spoke_wai_state_path.read_text())
    # Manually inject fake hub_path so get_hub_fingerprint tries to read it
    spoke_state_data['_hub_profile']['hub_config']['hub_path'] = str(hub_path) # Points to existing hub for valid path
    spoke_wai_state_path.write_text(json.dumps(spoke_state_data, indent=2))

    # Temporarily modify the hub's profile to return the fake fingerprint
    with patch('wai.hub.HubManager.get_hub_fingerprint', return_value=fake_fingerprint):
        # 2. Distribute a signed plan (will be signed with the REAL hub fingerprint)
        distribute_teach_command(spoke_path, hub_path, framework_path)
    
    # Get the REAL hub fingerprint (which the plan was signed with)
    real_fingerprint = HubManager().get_hub_fingerprint(hub_path)
    
    ingest_dir = spoke_path / "WAI-Spoke" / "seed" / "ingest"
    (ingest_dir / "manifest.json").write_text(json.dumps({"plan_teaching": {
        "path": "upgrade-adoption-plan.json",
        "safe_to_auto_adopt": True,
        "verification": {"hub_fingerprint": real_fingerprint}
    }}, indent=2))
    
    # Copy the plan into ingest as a teaching file
    shutil.copy2(spoke_path / 'upgrade-adoption-plan.json', ingest_dir / "plan_teaching.teaching")

    # 3. Perform adoption (with spoke *configured* for fake_fingerprint, plan *signed* with real_fingerprint)
    teaching_entry = {
        "id": "plan_teaching",
        "file_path": str(ingest_dir / "plan_teaching.teaching"),
        "metadata": {
            "path": "upgrade-adoption-plan.json",
            "safe_to_auto_adopt": True,
            "verification": {"hub_fingerprint": real_fingerprint}
        }
    }
    
    result = perform_teaching_adoption(spoke_path, teaching_entry)
    assert result is False # Expect refusal
    mock_print_error.assert_called_with(f"  [ERROR] Teaching plan fingerprint mismatch. Configured Hub: '{fake_fingerprint}', Plan signed by: '{real_fingerprint}'. Refusing adoption.")


@patch('wai.utils.input.print_success')
@patch('wai.utils.input.print_info')
@patch('wai.utils.input.print_error')
@patch('wai.utils.input.print_warning')
def test_perform_teaching_adoption_unsigned_plan_for_configured_spoke(
    mock_print_warning, mock_print_error, mock_print_info, mock_print_success,
    test_setup):
    """
    Ensures perform_teaching_adoption refuses when spoke is configured but plan is unsigned.
    """
    framework_path = test_setup["framework_path"]
    hub_path = test_setup["hub_path"]
    spoke_path = test_setup["spoke_path"]

    # 1. Configure spoke with hub's fingerprint
    hub_manager = HubManager()
    expected_fingerprint = hub_manager.get_hub_fingerprint(hub_path)
    spoke_wai_state_path = spoke_path / "WAI-Spoke" / "WAI-State.json"
    spoke_state_data = json.loads(spoke_wai_state_path.read_text())
    spoke_state_data['_hub_profile']['hub_config']['hub_path'] = str(hub_path)
    spoke_wai_state_path.write_text(json.dumps(spoke_state_data, indent=2))

    # 2. Distribute an UNSIGNED plan (simulated by removing verification after distribution)
    distribute_teach_command(spoke_path, hub_path, framework_path)
    plan_path = spoke_path / 'upgrade-adoption-plan.json'
    plan_data = json.loads(plan_path.read_text())
    del plan_data['verification'] # Simulate unsigned
    plan_path.write_text(json.dumps(plan_data, indent=2)) # Write unsigned plan back

    ingest_dir = spoke_path / "WAI-Spoke" / "seed" / "ingest"
    (ingest_dir / "manifest.json").write_text(json.dumps({"plan_teaching": {
        "path": "upgrade-adoption-plan.json",
        "safe_to_auto_adopt": True,
        # No verification in manifest metadata
    }}, indent=2))
    
    # Copy the unsigned plan into ingest as a teaching file
    shutil.copy2(plan_path, ingest_dir / "plan_teaching.teaching")

    # 3. Perform adoption
    teaching_entry = {
        "id": "plan_teaching",
        "file_path": str(ingest_dir / "plan_teaching.teaching"),
        "metadata": {
            "path": "upgrade-adoption-plan.json",
            "safe_to_auto_adopt": True,
            # No verification
        }
    }
    
    result = perform_teaching_adoption(spoke_path, teaching_entry)
    assert result is False # Expect refusal
    mock_print_error.assert_called_with(f"  [ERROR] Spoke configured with Hub fingerprint '{expected_fingerprint}', but teaching plan is not signed. Refusing adoption.")


@patch('wai.utils.input.print_success')
@patch('wai.utils.input.print_info')
@patch('wai.utils.input.print_error')
@patch('wai.utils.input.print_warning')
def test_perform_teaching_adoption_signed_plan_for_unconfigured_spoke(
    mock_print_warning, mock_print_error, mock_print_info, mock_print_success,
    test_setup):
    """
    Ensures perform_teaching_adoption proceeds with warning for signed plan on unconfigured spoke.
    """
    framework_path = test_setup["framework_path"]
    hub_path = test_setup["hub_path"]
    spoke_path = test_setup["spoke_path"]

    # 1. Spoke remains unconfigured for hub fingerprint (default setup)
    # Ensure its WAI-State.json's hub_path is empty or non-existent
    spoke_wai_state_path = spoke_path / "WAI-Spoke" / "WAI-State.json"
    spoke_state_data = json.loads(spoke_wai_state_path.read_text())
    spoke_state_data['_hub_profile']['hub_config']['hub_path'] = "" 
    spoke_wai_state_path.write_text(json.dumps(spoke_state_data, indent=2))

    # 2. Distribute a signed plan
    distribute_teach_command(spoke_path, hub_path, framework_path)
    plan_path = spoke_path / 'upgrade-adoption-plan.json'
    assert plan_path.exists()
    
    ingest_dir = spoke_path / "WAI-Spoke" / "seed" / "ingest"
    (ingest_dir / "manifest.json").write_text(json.dumps({"plan_teaching": {
        "path": "upgrade-adoption-plan.json",
        "safe_to_auto_adopt": True,
        "verification": json.loads(plan_path.read_text())['verification']
    }}, indent=2))
    
    # Copy the signed plan into ingest as a teaching file
    shutil.copy2(plan_path, ingest_dir / "plan_teaching.teaching")

    # 3. Perform adoption
    teaching_entry = {
        "id": "plan_teaching",
        "file_path": str(ingest_dir / "plan_teaching.teaching"),
        "metadata": {
            "path": "upgrade-adoption-plan.json",
            "safe_to_auto_adopt": True,
            "verification": json.loads(plan_path.read_text())['verification']
        }
    }
    
    result = perform_teaching_adoption(spoke_path, teaching_entry)
    assert result is True # Expect success with warning
    mock_print_warning.assert_called_with(f"  [WARNING] Spoke is not configured with a Hub fingerprint, but teaching plan is signed by '{json.loads(plan_path.read_text())['verification']['hub_fingerprint']}'. Proceeding with caution.")

