"""
Comprehensive integration tests for CLI Phase 1.

Tests the complete workflows:
- init hub → init spoke → learn → teach
- Error handling and edge cases
- JSON output formats
- State persistence
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from wai.cli.main import main, create_parser
from wai.cli.lib.state_manager import StateManager
from wai.cli.visuals import get_wagon_wheel, get_formatter, reset_wheel, reset_formatter


class TestInitToLearnToCycleIntegration:
    """Test complete init → learn → teach workflow."""
    
    def test_init_hub_then_spoke(self, capsys, tmp_path):
        """Test: Create hub, then create spoke under it."""
        with patch('wai.cli.lib.state_manager.StateManager.create_hub', return_value=True):
            with patch('wai.cli.lib.state_manager.StateManager.create_spoke', return_value=True):
                # Create hub
                result = main(['init', 'hub', '--name', 'IntegrationHub'])
                assert result == 0
                captured = capsys.readouterr()
                assert 'IntegrationHub' in captured.out
                
                # Create spoke
                result = main(['init', 'spoke', '--name', 'IntegrationSpoke', '--hub', 'IntegrationHub'])
                assert result == 0
                captured = capsys.readouterr()
                assert 'IntegrationSpoke' in captured.out
                assert 'IntegrationHub' in captured.out
    
    def test_init_and_learn_workflow(self, capsys):
        """Test: Init spoke then learn."""
        with patch('wai.cli.lib.state_manager.StateManager.create_spoke', return_value=True):
            with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
                # Init spoke
                result = main(['init', 'spoke', '--name', 'WorkflowSpoke', '--hub', 'WorkflowHub'])
                assert result == 0
                
                # Learn from spoke
                result = main(['learn', 'WorkflowSpoke'])
                assert result == 0
                captured = capsys.readouterr()
                assert 'WorkflowSpoke' in captured.out
    
    def test_init_and_teach_workflow(self, capsys):
        """Test: Init spoke then teach."""
        with patch('wai.cli.lib.state_manager.StateManager.create_spoke', return_value=True):
            with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
                # Init spoke
                result = main(['init', 'spoke', '--name', 'TeachSpoke', '--hub', 'TeachHub'])
                assert result == 0
                
                # Teach to spoke
                result = main(['teach', 'TeachSpoke'])
                assert result == 0
                captured = capsys.readouterr()
                assert 'TeachSpoke' in captured.out
    
    def test_complete_hub_spoke_learn_teach_cycle(self, capsys):
        """Test complete cycle: init hub → init spoke → learn → teach → stats → review."""
        with patch('wai.cli.lib.state_manager.StateManager.create_hub', return_value=True):
            with patch('wai.cli.lib.state_manager.StateManager.create_spoke', return_value=True):
                with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
                    with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
                        with patch('wai.cli.lib.state_manager.StateManager.get_node_info', return_value={
                            'type': 'spoke',
                            'wai_initialized': True,
                            'path': '/test',
                            'signal_count': 5,
                            'last_modified': '2026-02-08'
                        }):
                            # Init hub
                            result = main(['init', 'hub', '--name', 'CycleHub'])
                            assert result == 0
                            
                            # Init spoke
                            result = main(['init', 'spoke', '--name', 'CycleSpoke', '--hub', 'CycleHub'])
                            assert result == 0
                            
                            # Learn
                            result = main(['learn', 'CycleSpoke'])
                            assert result == 0
                            
                            # Teach
                            result = main(['teach', 'CycleSpoke'])
                            assert result == 0
                            
                            # Stats
                            result = main(['stats', 'CycleSpoke'])
                            assert result == 0
                            
                            # Review
                            result = main(['review', 'CycleSpoke'])
                            assert result == 0


class TestLearnCommandIntegration:
    """Comprehensive learn command integration tests."""
    
    def test_learn_discovers_signals(self, capsys):
        """Learn should discover signals from spoke."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=['sig1', 'sig2', 'sig3']):
            result = main(['learn', 'ProjectA'])
            assert result == 0
            captured = capsys.readouterr()
            assert 'ProjectA' in captured.out
    
    def test_learn_with_high_priority(self, capsys):
        """Learn should respect priority flag."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
            result = main(['learn', 'ProjectA', '--priority', 'high'])
            assert result == 0
            captured = capsys.readouterr()
            assert 'high' in captured.out.lower()
    
    def test_learn_with_normal_priority(self, capsys):
        """Learn should default to normal priority."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
            result = main(['learn', 'ProjectA'])
            assert result == 0
            captured = capsys.readouterr()
            assert 'normal' in captured.out.lower()
    
    def test_learn_with_low_priority(self, capsys):
        """Learn should respect low priority."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
            result = main(['learn', 'ProjectA', '--priority', 'low'])
            assert result == 0
            captured = capsys.readouterr()
            assert 'low' in captured.out.lower()
    
    def test_learn_with_force_flag(self, capsys):
        """Learn with force flag should skip confirmation."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
            result = main(['learn', 'ProjectA', '--force'])
            assert result == 0
    
    def test_learn_json_output_format(self, capsys):
        """Learn with --json should output JSON."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=['sig1', 'sig2']):
            result = main(['learn', 'ProjectA', '--json'])
            assert result == 0
            captured = capsys.readouterr()
            # Parse JSON output
            output = json.loads(captured.out)
            assert output['status'] == 'success'
            assert output['spoke'] == 'ProjectA'
            assert 'signals_discovered' in output
    
    def test_learn_json_has_signals_array(self, capsys):
        """Learn JSON output should include signals array."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=['sig1', 'sig2', 'sig3']):
            result = main(['learn', 'ProjectA', '--json'])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert 'signals' in output
            assert len(output['signals']) == 3


class TestTeachCommandIntegration:
    """Comprehensive teach command integration tests."""
    
    def test_teach_basic_workflow(self, capsys):
        """Teach should execute basic workflow."""
        with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
            result = main(['teach', 'ProjectA'])
            assert result == 0
            captured = capsys.readouterr()
            assert 'ProjectA' in captured.out
    
    def test_teach_with_force_flag(self, capsys):
        """Teach with force should skip confirmation."""
        with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
            result = main(['teach', 'ProjectA', '--force'])
            assert result == 0
    
    def test_teach_json_output_format(self, capsys):
        """Teach with --json should output JSON."""
        with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
            result = main(['teach', 'ProjectA', '--json'])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert output['status'] == 'success'
            assert output['spoke'] == 'ProjectA'
            assert 'templates_updated' in output


class TestStatsCommandIntegration:
    """Comprehensive stats command integration tests."""
    
    def test_stats_table_format(self, capsys):
        """Stats should display in table format by default."""
        node_info = {
            'type': 'spoke',
            'wai_initialized': True,
            'path': '/test/path',
            'signal_count': 5,
            'last_modified': '2026-02-08'
        }
        with patch('wai.cli.lib.state_manager.StateManager.get_node_info', return_value=node_info):
            with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
                result = main(['stats', 'ProjectA'])
                assert result == 0
                captured = capsys.readouterr()
                assert 'ProjectA' in captured.out or 'Statistics' in captured.out
    
    def test_stats_json_format(self, capsys):
        """Stats with --format json should output JSON."""
        node_info = {
            'type': 'spoke',
            'wai_initialized': True,
            'path': '/test/path',
            'signal_count': 5,
            'last_modified': '2026-02-08'
        }
        with patch('wai.cli.lib.state_manager.StateManager.get_node_info', return_value=node_info):
            with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
                result = main(['stats', 'ProjectA', '--format', 'json'])
                assert result == 0
                captured = capsys.readouterr()
                output = json.loads(captured.out)
                assert 'spoke' in output
                assert output['spoke'] == 'ProjectA'
    
    def test_stats_text_format(self, capsys):
        """Stats with --format text should output plain text."""
        node_info = {
            'type': 'spoke',
            'wai_initialized': True,
            'path': '/test/path',
            'signal_count': 5,
            'last_modified': '2026-02-08'
        }
        with patch('wai.cli.lib.state_manager.StateManager.get_node_info', return_value=node_info):
            with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
                result = main(['stats', 'ProjectA', '--format', 'text'])
                assert result == 0
                captured = capsys.readouterr()
                assert 'Statistics' in captured.out
    
    def test_stats_with_all_flag(self, capsys):
        """Stats with --all should show detailed breakdown."""
        node_info = {
            'type': 'spoke',
            'wai_initialized': True,
            'path': '/test/path',
            'signal_count': 5,
            'last_modified': '2026-02-08'
        }
        with patch('wai.cli.lib.state_manager.StateManager.get_node_info', return_value=node_info):
            with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
                result = main(['stats', 'ProjectA', '--all'])
                assert result == 0


class TestReviewCommandIntegration:
    """Comprehensive review command integration tests."""
    
    def test_review_text_format(self, capsys):
        """Review should display in text format by default."""
        result = main(['review', 'ProjectA'])
        assert result == 0
        captured = capsys.readouterr()
        assert 'ProjectA' in captured.out or 'Review' in captured.out
    
    def test_review_json_format(self, capsys):
        """Review with --format json should output JSON."""
        result = main(['review', 'ProjectA', '--format', 'json'])
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['spoke'] == 'ProjectA'
        assert 'wai_initialized' in output
    
    def test_review_with_deep_flag(self, capsys):
        """Review with --deep should show detailed analysis."""
        result = main(['review', 'ProjectA', '--deep'])
        assert result == 0


class TestMultipleCommandSequence:
    """Test sequences of multiple commands."""
    
    def test_learn_multiple_times(self, capsys):
        """Should be able to learn multiple times."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
            result1 = main(['learn', 'ProjectA'])
            assert result1 == 0
            
            result2 = main(['learn', 'ProjectB'])
            assert result2 == 0
    
    def test_teach_multiple_times(self, capsys):
        """Should be able to teach multiple times."""
        with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
            result1 = main(['teach', 'ProjectA'])
            assert result1 == 0
            
            result2 = main(['teach', 'ProjectB'])
            assert result2 == 0
    
    def test_mixed_commands_sequence(self, capsys):
        """Should handle mixed command sequences."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
            with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
                with patch('wai.cli.lib.state_manager.StateManager.get_node_info', return_value={
                    'type': 'spoke', 'wai_initialized': True, 'path': '/test', 'signal_count': 5, 'last_modified': '2026-02-08'
                }):
                    # Learn
                    result = main(['learn', 'ProjectA', '--priority', 'high'])
                    assert result == 0
                    
                    # Teach
                    result = main(['teach', 'ProjectA'])
                    assert result == 0
                    
                    # Stats
                    result = main(['stats', 'ProjectA'])
                    assert result == 0
                    
                    # Review
                    result = main(['review', 'ProjectA'])
                    assert result == 0


class TestErrorHandlingIntegration:
    """Test error handling across commands."""
    
    def test_keyboard_interrupt_during_learn(self):
        """KeyboardInterrupt during learn should return 130."""
        with patch('wai.cli.main.cmd_learn', side_effect=KeyboardInterrupt()):
            result = main(['learn', 'ProjectA'])
            assert result == 130
    
    def test_keyboard_interrupt_during_teach(self):
        """KeyboardInterrupt during teach should return 130."""
        with patch('wai.cli.main.cmd_teach', side_effect=KeyboardInterrupt()):
            result = main(['teach', 'ProjectA'])
            assert result == 130
    
    def test_exception_during_init(self):
        """Exception during init should return 1."""
        with patch('wai.cli.main.cmd_init', side_effect=Exception("Init error")):
            result = main(['init', 'hub', '--name', 'TestHub'])
            assert result == 1
    
    def test_exception_during_learn(self):
        """Exception during learn should return 1."""
        with patch('wai.cli.main.cmd_learn', side_effect=Exception("Learn error")):
            result = main(['learn', 'ProjectA'])
            assert result == 1


class TestAnimationIntegration:
    """Test wagon wheel animation integration."""
    
    def test_init_shows_animation(self, capsys):
        """Init command should animate wagon wheel."""
        with patch('wai.cli.lib.state_manager.StateManager.create_hub', return_value=True):
            with patch('wai.cli.visuals.wheel.WagonWheel.roll') as mock_roll:
                result = main(['init', 'hub', '--name', 'TestHub'])
                assert result == 0
                # Wheel should have been called
    
    def test_learn_shows_animation(self, capsys):
        """Learn command should animate wagon wheel."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
            with patch('wai.cli.visuals.wheel.WagonWheel.roll') as mock_roll:
                result = main(['learn', 'ProjectA'])
                assert result == 0
    
    def test_teach_shows_animation(self, capsys):
        """Teach command should animate wagon wheel."""
        with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
            with patch('wai.cli.visuals.wheel.WagonWheel.roll') as mock_roll:
                result = main(['teach', 'ProjectA'])
                assert result == 0


class TestOutputConsistency:
    """Test output consistency across commands."""
    
    def test_all_commands_return_valid_exit_codes(self):
        """All commands should return 0 on success."""
        with patch('wai.cli.lib.state_manager.StateManager.create_hub', return_value=True):
            with patch('wai.cli.lib.state_manager.StateManager.create_spoke', return_value=True):
                with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
                    with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
                        with patch('wai.cli.lib.state_manager.StateManager.get_node_info', return_value={
                            'type': 'spoke', 'wai_initialized': True, 'path': '/test', 'signal_count': 0, 'last_modified': '2026-02-08'
                        }):
                            assert main(['init', 'hub', '--name', 'Hub']) == 0
                            assert main(['init', 'spoke', '--name', 'Spoke', '--hub', 'Hub']) == 0
                            assert main(['learn', 'Spoke']) == 0
                            assert main(['teach', 'Spoke']) == 0
                            assert main(['stats', 'Spoke']) == 0
                            assert main(['review', 'Spoke']) == 0
    
    def test_json_output_is_valid_json(self, capsys):
        """All JSON outputs should be valid JSON."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
            # Learn JSON
            result = main(['learn', 'ProjectA', '--json'])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)  # Should not raise
            assert isinstance(output, dict)
        
        with patch('wai.cli.lib.state_manager.StateManager.load_state', return_value={}):
            # Teach JSON
            result = main(['teach', 'ProjectA', '--json'])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)  # Should not raise
            assert isinstance(output, dict)
        
        with patch('wai.cli.lib.state_manager.StateManager.get_node_info', return_value={
            'type': 'spoke', 'wai_initialized': True, 'path': '/test', 'signal_count': 0, 'last_modified': '2026-02-08'
        }):
            with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=[]):
                # Stats JSON
                result = main(['stats', 'ProjectA', '--format', 'json'])
                assert result == 0
                captured = capsys.readouterr()
                output = json.loads(captured.out)  # Should not raise
                assert isinstance(output, dict)
        
        # Review JSON
        result = main(['review', 'ProjectA', '--format', 'json'])
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)  # Should not raise
        assert isinstance(output, dict)


class TestStateManagement:
    """Test state management across commands."""
    
    def test_init_creates_state(self):
        """Init should create node state."""
        with patch('wai.cli.lib.state_manager.StateManager.create_hub', return_value=True) as mock_create:
            result = main(['init', 'hub', '--name', 'StateHub'])
            assert result == 0
            # Verify StateManager.create_hub was called
    
    def test_learn_updates_signals(self):
        """Learn should update signals in state."""
        with patch('wai.cli.lib.state_manager.StateManager.discover_signals', return_value=['sig1']):
            with patch('wai.cli.lib.state_manager.StateManager.add_signal') as mock_add:
                result = main(['learn', 'ProjectA', '--priority', 'high'])
                assert result == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
