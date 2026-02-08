"""
Tests for state manager module.

Comprehensive tests for:
- State loading/saving
- Signal management
- Hub/spoke creation
- Node detection
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from wai.cli.lib.state_manager import StateManager, get_state_manager, reset_manager


class TestStateManagerInitialization:
    """Test state manager initialization."""
    
    def test_state_manager_created(self, temp_workspace):
        """Should create state manager."""
        manager = StateManager(node_path=temp_workspace)
        assert manager is not None
    
    def test_detects_node_type_unknown(self, temp_workspace):
        """Should detect unknown node type."""
        manager = StateManager(node_path=temp_workspace)
        assert manager.node_type == 'unknown'
    
    def test_detects_hub_marker(self, temp_workspace):
        """Should detect hub by marker."""
        (temp_workspace / '.hub').touch()
        manager = StateManager(node_path=temp_workspace)
        assert manager.node_type == 'hub'
    
    def test_detects_spoke_marker(self, temp_workspace):
        """Should detect spoke by WAI-Spoke."""
        (temp_workspace / 'WAI-Spoke').mkdir()
        manager = StateManager(node_path=temp_workspace)
        assert manager.node_type == 'spoke'


class TestStateLoading:
    """Test state loading."""
    
    def test_load_default_state(self, temp_workspace):
        """Should load default state if no file."""
        manager = StateManager(node_path=temp_workspace)
        state = manager.load_state()
        assert state is not None
        assert 'wheel' in state
    
    def test_load_existing_state(self, temp_workspace):
        """Should load existing state file."""
        # Create spoke with state
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        state_file = wai_spoke / 'WAI-State.json'
        test_state = {"wheel": {"name": "TestSpoke"}}
        with open(state_file, 'w') as f:
            json.dump(test_state, f)
        
        manager = StateManager(node_path=temp_workspace)
        state = manager.load_state()
        assert state['wheel']['name'] == 'TestSpoke'


class TestStateSaving:
    """Test state saving."""
    
    def test_save_state(self, temp_workspace):
        """Should save state to file."""
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        manager = StateManager(node_path=temp_workspace)
        test_state = {"wheel": {"name": "TestSpoke"}}
        
        result = manager.save_state(test_state)
        assert result is True
        
        # Verify file exists
        state_file = wai_spoke / 'WAI-State.json'
        assert state_file.exists()
    
    def test_save_creates_backup(self, temp_workspace):
        """Should create backup when saving."""
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        manager = StateManager(node_path=temp_workspace)
        
        # Save first time
        manager.save_state({"test": "data"})
        
        # Save second time
        manager.save_state({"test": "data2"})
        
        # Backup should exist
        backup_file = wai_spoke / 'WAI-State.json.bak'
        assert backup_file.exists()


class TestSignalDiscovery:
    """Test signal discovery and management."""
    
    def test_discover_no_signals(self, temp_workspace):
        """Should handle no signals."""
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        manager = StateManager(node_path=temp_workspace)
        signals = manager.discover_signals()
        assert signals == []
    
    def test_discover_existing_signals(self, temp_workspace):
        """Should discover existing signals."""
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        # Create signals file
        signals_file = wai_spoke / 'WAI-Signals.jsonl'
        with open(signals_file, 'w') as f:
            f.write(json.dumps({"type": "test", "value": 1}) + '\n')
            f.write(json.dumps({"type": "test", "value": 2}) + '\n')
        
        manager = StateManager(node_path=temp_workspace)
        signals = manager.discover_signals()
        assert len(signals) == 2
        assert signals[0]['value'] == 1
    
    def test_add_signal(self, temp_workspace):
        """Should add signal to file."""
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        manager = StateManager(node_path=temp_workspace)
        signal = {"type": "test", "data": "value"}
        
        result = manager.add_signal(signal)
        assert result is True
        
        # Verify file has signal
        signals_file = wai_spoke / 'WAI-Signals.jsonl'
        assert signals_file.exists()
        
        with open(signals_file, 'r') as f:
            line = f.readline()
            saved_signal = json.loads(line)
            assert saved_signal['type'] == 'test'


class TestNodeInfo:
    """Test node information retrieval."""
    
    def test_get_node_info_unknown(self, temp_workspace):
        """Should get info for unknown node."""
        manager = StateManager(node_path=temp_workspace)
        info = manager.get_node_info()
        assert info['type'] == 'unknown'
        assert info['wai_initialized'] is False
    
    def test_get_node_info_spoke(self, temp_workspace):
        """Should get info for spoke."""
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        manager = StateManager(node_path=temp_workspace)
        info = manager.get_node_info()
        assert info['type'] == 'spoke'
        assert info['wai_initialized'] is True
    
    def test_node_info_includes_signals(self, temp_workspace):
        """Node info should include signal count."""
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        # Add signals
        signals_file = wai_spoke / 'WAI-Signals.jsonl'
        with open(signals_file, 'w') as f:
            f.write(json.dumps({"type": "test"}) + '\n')
            f.write(json.dumps({"type": "test"}) + '\n')
        
        manager = StateManager(node_path=temp_workspace)
        info = manager.get_node_info()
        assert info['signal_count'] == 2


class TestMetadataUpdate:
    """Test metadata update."""
    
    def test_update_name(self, temp_workspace):
        """Should update node name."""
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        manager = StateManager(node_path=temp_workspace)
        result = manager.update_node_metadata(name="NewName")
        assert result is True
        
        # Verify
        state = manager.load_state()
        assert state['wheel']['name'] == 'NewName'
    
    def test_update_description(self, temp_workspace):
        """Should update node description."""
        wai_spoke = temp_workspace / 'WAI-Spoke'
        wai_spoke.mkdir()
        
        manager = StateManager(node_path=temp_workspace)
        manager.update_node_metadata(description="New Description")
        
        state = manager.load_state()
        assert state['wheel']['description'] == 'New Description'


class TestHubCreation:
    """Test hub creation."""
    
    def test_create_hub(self, temp_workspace):
        """Should create hub."""
        hub_path = temp_workspace / 'hub'
        result = StateManager.create_hub(hub_path, 'TestHub')
        assert result is True
        
        # Verify marker
        assert (hub_path / '.hub').exists()
        
        # Verify profile
        profile_file = hub_path / 'hub-profile.json'
        assert profile_file.exists()
    
    def test_create_hub_with_description(self, temp_workspace):
        """Should create hub with description."""
        hub_path = temp_workspace / 'hub'
        result = StateManager.create_hub(hub_path, 'TestHub', 'Test Description')
        assert result is True
        
        with open(hub_path / 'hub-profile.json', 'r') as f:
            profile = json.load(f)
            assert profile['description'] == 'Test Description'


class TestSpokeCreation:
    """Test spoke creation."""
    
    def test_create_spoke(self, temp_workspace):
        """Should create spoke."""
        spoke_path = temp_workspace / 'spoke'
        result = StateManager.create_spoke(spoke_path, 'TestSpoke', 'TestHub')
        assert result is True
        
        # Verify structure
        assert (spoke_path / 'WAI-Spoke').exists()
        assert (spoke_path / 'WAI-Spoke' / 'WAI-State.json').exists()
    
    def test_create_spoke_files(self, temp_workspace):
        """Should create all spoke files."""
        spoke_path = temp_workspace / 'spoke'
        StateManager.create_spoke(spoke_path, 'TestSpoke', 'TestHub')
        
        wai_spoke = spoke_path / 'WAI-Spoke'
        assert (wai_spoke / 'WAI-Signals.jsonl').exists()
        assert (wai_spoke / 'WAI-Lugs.jsonl').exists()
        assert (wai_spoke / 'WAI-Session-Log.jsonl').exists()
    
    def test_spoke_state_has_hub_id(self, temp_workspace):
        """Spoke state should reference hub."""
        spoke_path = temp_workspace / 'spoke'
        StateManager.create_spoke(spoke_path, 'TestSpoke', 'TestHub')
        
        with open(spoke_path / 'WAI-Spoke' / 'WAI-State.json', 'r') as f:
            state = json.load(f)
            assert state['wheel']['hub_id'] == 'TestHub'


class TestSingleton:
    """Test singleton pattern."""
    
    def test_get_manager_returns_instance(self):
        """Should return state manager instance."""
        reset_manager()
        manager = get_state_manager()
        assert isinstance(manager, StateManager)
    
    def test_get_manager_caches(self):
        """Should cache manager instance."""
        reset_manager()
        mgr1 = get_state_manager()
        mgr2 = get_state_manager()
        assert mgr1 is mgr2
    
    def test_reset_manager(self):
        """Should reset singleton."""
        reset_manager()
        mgr1 = get_state_manager()
        reset_manager()
        mgr2 = get_state_manager()
        assert mgr1 is not mgr2


class TestIntegration:
    """Integration tests."""
    
    def test_full_spoke_workflow(self, temp_workspace):
        """Test complete spoke workflow."""
        # Create spoke
        StateManager.create_spoke(temp_workspace, 'TestSpoke', 'TestHub')
        
        # Load manager
        manager = StateManager(node_path=temp_workspace)
        
        # Add signal
        manager.add_signal({"type": "test"})
        
        # Discover signals
        signals = manager.discover_signals()
        assert len(signals) > 0
        
        # Get info
        info = manager.get_node_info()
        assert info['wai_initialized'] is True
    
    def test_full_hub_workflow(self, temp_workspace):
        """Test complete hub workflow."""
        # Create hub
        StateManager.create_hub(temp_workspace, 'TestHub')
        
        # Load manager
        manager = StateManager(node_path=temp_workspace)
        assert manager.node_type == 'hub'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
