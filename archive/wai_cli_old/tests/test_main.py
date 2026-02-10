"""
Tests for CLI main entry point.

Comprehensive tests for:
- Command parsing
- Command routing
- Integration with modules
- Error handling
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from wai.cli.main import main, create_parser, cmd_init, cmd_learn, cmd_teach, cmd_stats, cmd_review


class TestMainParser:
    """Test argument parser creation."""
    
    def test_parser_created(self):
        """Parser should be created without errors."""
        parser = create_parser()
        assert parser is not None
    
    def test_parser_has_verbs(self):
        """Parser should have verb subparsers."""
        parser = create_parser()
        # Parse help to verify structure
        help_text = parser.format_help()
        assert 'init' in help_text
        assert 'learn' in help_text
        assert 'teach' in help_text
        assert 'stats' in help_text
        assert 'review' in help_text
    
    def test_parse_init_hub(self):
        """Should parse init hub command."""
        parser = create_parser()
        args = parser.parse_args(['init', 'hub', '--name', 'TestHub'])
        assert args.verb == 'init'
        assert args.node_type == 'hub'
        assert args.name == 'TestHub'
    
    def test_parse_init_spoke(self):
        """Should parse init spoke command."""
        parser = create_parser()
        args = parser.parse_args(['init', 'spoke', '--name', 'TestSpoke', '--hub', 'TestHub'])
        assert args.verb == 'init'
        assert args.node_type == 'spoke'
        assert args.name == 'TestSpoke'
        assert args.hub == 'TestHub'
    
    def test_parse_learn(self):
        """Should parse learn command."""
        parser = create_parser()
        args = parser.parse_args(['learn', 'ProjectA'])
        assert args.verb == 'learn'
        assert args.spoke == 'ProjectA'
    
    def test_parse_learn_with_priority(self):
        """Should parse learn with priority."""
        parser = create_parser()
        args = parser.parse_args(['learn', 'ProjectA', '--priority', 'high'])
        assert args.priority == 'high'
    
    def test_parse_learn_with_force(self):
        """Should parse learn with force flag."""
        parser = create_parser()
        args = parser.parse_args(['learn', 'ProjectA', '--force'])
        assert args.force is True
    
    def test_parse_teach(self):
        """Should parse teach command."""
        parser = create_parser()
        args = parser.parse_args(['teach', 'ProjectA'])
        assert args.verb == 'teach'
        assert args.spoke == 'ProjectA'
    
    def test_parse_stats(self):
        """Should parse stats command."""
        parser = create_parser()
        args = parser.parse_args(['stats', 'ProjectA'])
        assert args.verb == 'stats'
        assert args.spoke == 'ProjectA'
    
    def test_parse_stats_with_format(self):
        """Should parse stats with format."""
        parser = create_parser()
        args = parser.parse_args(['stats', 'ProjectA', '--format', 'json'])
        assert args.format == 'json'
    
    def test_parse_review(self):
        """Should parse review command."""
        parser = create_parser()
        args = parser.parse_args(['review', 'ProjectA'])
        assert args.verb == 'review'
        assert args.spoke == 'ProjectA'
    
    def test_version_flag(self):
        """Should handle --version flag."""
        parser = create_parser()
        # --version exits, so we just check it's in help
        help_text = parser.format_help()
        assert '--version' in help_text


class TestCommandInit:
    """Test init command."""
    
    def test_init_hub(self, capsys):
        """Should initialize hub."""
        parser = create_parser()
        args = parser.parse_args(['init', 'hub', '--name', 'TestHub'])
        result = cmd_init(args)
        assert result == 0
        captured = capsys.readouterr()
        assert 'TestHub' in captured.out
    
    def test_init_spoke(self, capsys):
        """Should initialize spoke."""
        parser = create_parser()
        args = parser.parse_args(['init', 'spoke', '--name', 'TestSpoke', '--hub', 'TestHub'])
        result = cmd_init(args)
        assert result == 0
        captured = capsys.readouterr()
        assert 'TestSpoke' in captured.out


class TestCommandLearn:
    """Test learn command."""
    
    def test_learn_basic(self, capsys):
        """Should execute learn command."""
        parser = create_parser()
        args = parser.parse_args(['learn', 'ProjectA'])
        result = cmd_learn(args)
        assert result == 0
        captured = capsys.readouterr()
        assert 'ProjectA' in captured.out
    
    def test_learn_with_priority(self, capsys):
        """Should respect priority flag."""
        parser = create_parser()
        args = parser.parse_args(['learn', 'ProjectA', '--priority', 'high'])
        result = cmd_learn(args)
        assert result == 0
        captured = capsys.readouterr()
        assert 'high' in captured.out.lower()
    
    def test_learn_json_output(self, capsys):
        """Should output JSON when requested."""
        parser = create_parser()
        args = parser.parse_args(['learn', 'ProjectA', '--json'])
        result = cmd_learn(args)
        assert result == 0
        captured = capsys.readouterr()
        # Should be valid JSON
        output = json.loads(captured.out)
        assert output['status'] == 'success'
        assert output['spoke'] == 'ProjectA'


class TestCommandTeach:
    """Test teach command."""
    
    def test_teach_basic(self, capsys):
        """Should execute teach command."""
        parser = create_parser()
        args = parser.parse_args(['teach', 'ProjectA'])
        result = cmd_teach(args)
        assert result == 0
        captured = capsys.readouterr()
        assert 'ProjectA' in captured.out
    
    def test_teach_json_output(self, capsys):
        """Should output JSON when requested."""
        parser = create_parser()
        args = parser.parse_args(['teach', 'ProjectA', '--json'])
        result = cmd_teach(args)
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['status'] == 'success'


class TestCommandStats:
    """Test stats command."""
    
    def test_stats_basic(self, capsys):
        """Should execute stats command."""
        parser = create_parser()
        args = parser.parse_args(['stats', 'ProjectA'])
        result = cmd_stats(args)
        assert result == 0
        captured = capsys.readouterr()
        assert 'ProjectA' in captured.out or 'Statistics' in captured.out
    
    def test_stats_json_format(self, capsys):
        """Should output JSON format."""
        parser = create_parser()
        args = parser.parse_args(['stats', 'ProjectA', '--format', 'json'])
        result = cmd_stats(args)
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'spoke' in output
    
    def test_stats_table_format(self, capsys):
        """Should output table format."""
        parser = create_parser()
        args = parser.parse_args(['stats', 'ProjectA', '--format', 'table'])
        result = cmd_stats(args)
        assert result == 0
        captured = capsys.readouterr()
        assert 'ProjectA' in captured.out


class TestCommandReview:
    """Test review command."""
    
    def test_review_basic(self, capsys):
        """Should execute review command."""
        parser = create_parser()
        args = parser.parse_args(['review', 'ProjectA'])
        result = cmd_review(args)
        assert result == 0
        captured = capsys.readouterr()
        assert 'ProjectA' in captured.out or 'Review' in captured.out
    
    def test_review_json_output(self, capsys):
        """Should output JSON when requested."""
        parser = create_parser()
        args = parser.parse_args(['review', 'ProjectA', '--json'])
        result = cmd_review(args)
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['spoke'] == 'ProjectA'


class TestMainEntryPoint:
    """Test main entry point."""
    
    def test_main_no_args_shows_help(self, capsys):
        """main() with no args should show welcome banner."""
        result = main([])
        assert result == 0
    
    def test_main_init_hub(self, capsys):
        """main() should route init hub command."""
        result = main(['init', 'hub', '--name', 'TestHub'])
        assert result == 0
    
    def test_main_learn(self, capsys):
        """main() should route learn command."""
        result = main(['learn', 'ProjectA'])
        assert result == 0
    
    def test_main_teach(self, capsys):
        """main() should route teach command."""
        result = main(['teach', 'ProjectA'])
        assert result == 0
    
    def test_main_stats(self, capsys):
        """main() should route stats command."""
        result = main(['stats', 'ProjectA'])
        assert result == 0
    
    def test_main_review(self, capsys):
        """main() should route review command."""
        result = main(['review', 'ProjectA'])
        assert result == 0
    
    def test_main_invalid_command(self, capsys):
        """main() should handle invalid command."""
        result = main(['invalid'])
        # Should show error or help
        assert result in [0, 1, 2]  # Exit codes for help/error
    
    def test_main_help_flag(self, capsys):
        """main() should show help with --help."""
        with pytest.raises(SystemExit):
            main(['--help'])
    
    def test_main_version_flag(self, capsys):
        """main() should show version with --version."""
        with pytest.raises(SystemExit):
            main(['--version'])


class TestErrorHandling:
    """Test error handling."""
    
    def test_keyboard_interrupt(self):
        """main() should handle KeyboardInterrupt gracefully."""
        with patch('wai.cli.main.cmd_learn', side_effect=KeyboardInterrupt()):
            result = main(['learn', 'ProjectA'])
            assert result == 130  # KeyboardInterrupt exit code
    
    def test_general_exception(self):
        """main() should handle general exceptions."""
        with patch('wai.cli.main.cmd_learn', side_effect=Exception("Test error")):
            result = main(['learn', 'ProjectA'])
            assert result == 1


class TestIntegration:
    """Integration tests."""
    
    def test_full_workflow(self, capsys):
        """Test complete workflow."""
        # Initialize hub
        result = main(['init', 'hub', '--name', 'TestHub'])
        assert result == 0
        
        # Initialize spoke
        result = main(['init', 'spoke', '--name', 'TestSpoke', '--hub', 'TestHub'])
        assert result == 0
        
        # Learn
        result = main(['learn', 'TestSpoke'])
        assert result == 0
        
        # Teach
        result = main(['teach', 'TestSpoke'])
        assert result == 0
    
    def test_json_workflow(self, capsys):
        """Test JSON output workflow."""
        result = main(['learn', 'ProjectA', '--json'])
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'status' in output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
