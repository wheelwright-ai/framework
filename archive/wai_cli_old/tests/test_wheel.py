"""
Tests for wagon wheel animation module.

Comprehensive test suite covering:
- Frame rendering
- Animation execution
- Speed configuration
- TTY detection
- Graceful degradation
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

from wai.cli.visuals.wheel import WagonWheel, get_wagon_wheel, reset_wheel


class TestWagonWheelFrames:
    """Test frame rendering."""
    
    def test_wheel_has_12_frames(self):
        """Wagon wheel should have 12 frames."""
        wheel = WagonWheel(enabled=False)
        assert len(wheel.FRAMES) == 12
    
    def test_frames_are_strings(self):
        """All frames should be strings."""
        wheel = WagonWheel(enabled=False)
        for frame in wheel.FRAMES:
            assert isinstance(frame, str)
    
    def test_get_frame_returns_correct_frame(self):
        """get_frame should return the correct frame."""
        wheel = WagonWheel(width=60, enabled=False)
        frame = wheel.get_frame(0)
        assert isinstance(frame, str)
        assert len(frame) <= 60
    
    def test_get_frame_pads_to_width(self):
        """get_frame should pad to specified width."""
        wheel = WagonWheel(width=60, enabled=False)
        frame = wheel.get_frame(0)
        assert len(frame) == 60
    
    def test_get_frame_cycles(self):
        """get_frame should cycle through frames."""
        wheel = WagonWheel(width=60, enabled=False)
        frame0 = wheel.get_frame(0)
        frame12 = wheel.get_frame(12)  # Should be same as frame 0
        assert frame0 == frame12
    
    def test_render_all_frames(self):
        """render_all_frames should return all frames."""
        wheel = WagonWheel(width=60, enabled=False)
        frames = wheel.render_all_frames()
        assert len(frames) == 12
        assert all(len(f) == 60 for f in frames)


class TestWagonWheelAnimation:
    """Test animation execution."""
    
    @patch('sys.stdout')
    def test_roll_animation_executes(self, mock_stdout):
        """roll should execute without errors."""
        wheel = WagonWheel(width=60, enabled=True)
        wheel.roll(duration_ms=100)  # Short duration for testing
        # Should have written to stdout
        assert mock_stdout.write.called
    
    @patch('sys.stdout')
    def test_roll_disabled_in_non_tty(self, mock_stdout):
        """roll should not animate in non-TTY."""
        wheel = WagonWheel(width=60, enabled=False)
        wheel.roll(duration_ms=100)
        # Should not write when disabled
        assert not mock_stdout.write.called
    
    @patch('sys.stdout')
    def test_pulse_animation_executes(self, mock_stdout):
        """pulse should execute without errors."""
        wheel = WagonWheel(width=60, enabled=True)
        wheel.pulse()
        assert mock_stdout.write.called
    
    @patch('sys.stdout')
    def test_roll_clears_line_after(self, mock_stdout):
        """roll should clear the line after animation."""
        wheel = WagonWheel(width=60, enabled=True)
        wheel.roll(duration_ms=50)
        # Check that spaces were written to clear
        calls = [str(call) for call in mock_stdout.write.call_args_list]
        # Should have space-clearing call
        assert any(' ' * 60 in str(call) for call in calls)


class TestWagonWheelSpeed:
    """Test speed configuration."""
    
    def test_fast_speed(self):
        """Fast speed should set correct delay."""
        wheel = WagonWheel(speed='fast', enabled=False)
        assert wheel.frame_delay == 0.05
    
    def test_medium_speed(self):
        """Medium speed should set correct delay."""
        wheel = WagonWheel(speed='medium', enabled=False)
        assert wheel.frame_delay == 0.08
    
    def test_slow_speed(self):
        """Slow speed should set correct delay."""
        wheel = WagonWheel(speed='slow', enabled=False)
        assert wheel.frame_delay == 0.12
    
    def test_unknown_speed_defaults_to_medium(self):
        """Unknown speed should default to medium."""
        wheel = WagonWheel(speed='unknown', enabled=False)
        assert wheel.frame_delay == 0.08


class TestWagonWheelTTYDetection:
    """Test TTY detection and graceful degradation."""
    
    @patch('sys.stdout')
    def test_detects_tty_correctly(self, mock_stdout):
        """Should detect TTY from stdout."""
        mock_stdout.isatty.return_value = True
        wheel = WagonWheel(enabled=True)
        # If isatty returns True and enabled=True, wheel should be enabled
        assert wheel.enabled or not wheel._is_tty()
    
    @patch('sys.stdout')
    def test_detects_non_tty_correctly(self, mock_stdout):
        """Should detect non-TTY environments."""
        mock_stdout.isatty.return_value = False
        wheel = WagonWheel(enabled=True)
        assert not wheel.enabled
    
    def test_enabled_false_disables_animation(self):
        """enabled=False should disable animation."""
        wheel = WagonWheel(enabled=False)
        assert not wheel.enabled
    
    def test_enabled_true_respects_tty_status(self):
        """enabled=True should respect TTY status."""
        with patch('sys.stdout') as mock_stdout:
            mock_stdout.isatty.return_value = False
            wheel = WagonWheel(enabled=True)
            # Should be disabled if not TTY
            assert not wheel.enabled


class TestWagonWheelSingleton:
    """Test singleton pattern."""
    
    def test_get_wagon_wheel_returns_instance(self):
        """get_wagon_wheel should return WagonWheel instance."""
        reset_wheel()
        wheel = get_wagon_wheel()
        assert isinstance(wheel, WagonWheel)
    
    def test_get_wagon_wheel_returns_same_instance(self):
        """get_wagon_wheel should return same instance on second call."""
        reset_wheel()
        wheel1 = get_wagon_wheel()
        wheel2 = get_wagon_wheel()
        assert wheel1 is wheel2
    
    def test_reset_wheel_clears_singleton(self):
        """reset_wheel should clear singleton."""
        reset_wheel()
        wheel1 = get_wagon_wheel()
        reset_wheel()
        wheel2 = get_wagon_wheel()
        assert wheel1 is not wheel2
    
    def test_get_wagon_wheel_respects_config(self):
        """get_wagon_wheel should accept configuration."""
        reset_wheel()
        wheel = get_wagon_wheel(width=80, speed='fast', enabled=False)
        assert wheel.width == 80
        assert wheel.speed == 'fast'
        assert not wheel.enabled


class TestWagonWheelErrorHandling:
    """Test error handling and edge cases."""
    
    @patch('sys.stdout')
    def test_keyboard_interrupt_handled(self, mock_stdout):
        """roll should handle KeyboardInterrupt gracefully."""
        mock_stdout.write.side_effect = KeyboardInterrupt()
        wheel = WagonWheel(width=60, enabled=True)
        # Should not raise exception
        try:
            wheel.roll(duration_ms=100)
        except KeyboardInterrupt:
            pytest.fail("KeyboardInterrupt should be handled")
    
    def test_negative_duration(self):
        """roll should handle negative duration."""
        wheel = WagonWheel(enabled=False)
        # Should not crash with negative duration
        wheel.roll(duration_ms=-100)
    
    def test_zero_duration(self):
        """roll should handle zero duration."""
        wheel = WagonWheel(enabled=False)
        # Should not crash with zero duration
        wheel.roll(duration_ms=0)
    
    def test_very_large_duration(self):
        """roll should handle very large duration gracefully."""
        wheel = WagonWheel(enabled=False)
        # Should not crash with large duration
        wheel.roll(duration_ms=999999)


class TestWagonWheelConfiguration:
    """Test configuration options."""
    
    def test_custom_width(self):
        """Should accept custom width."""
        wheel = WagonWheel(width=80, enabled=False)
        assert wheel.width == 80
        frame = wheel.get_frame(0)
        assert len(frame) == 80
    
    def test_custom_frames(self):
        """Should accept custom frame count."""
        wheel = WagonWheel(frames=20, enabled=False)
        # Still uses standard frames, but this tests the parameter
        assert wheel.frames == 20
    
    def test_default_configuration(self):
        """Should have reasonable defaults."""
        wheel = WagonWheel(enabled=False)
        assert wheel.width == 60
        assert wheel.frames == 12
        assert wheel.speed == 'medium'


class TestWagonWheelOutput:
    """Test output formatting."""
    
    def test_frame_output_format(self):
        """Frames should be properly formatted."""
        wheel = WagonWheel(width=60, enabled=False)
        frame = wheel.get_frame(0)
        # Should be a string of correct length
        assert isinstance(frame, str)
        assert len(frame) == 60
        # Should contain wheel character
        assert '◎' in wheel.FRAMES[0] or '◐' in wheel.FRAMES[0]
    
    def test_all_frames_contain_wheel_chars(self):
        """All frames should contain wheel characters."""
        wheel = WagonWheel(enabled=False)
        wheel_chars = {'◎', '◐', '◑', '◒', '◓', '◔', '◕', '◖', '◉'}
        for frame in wheel.FRAMES:
            # Each frame should contain at least one wheel character
            assert any(char in frame for char in wheel_chars), f"Frame missing wheel: {frame}"


# Integration tests
class TestWagonWheelIntegration:
    """Integration tests for wagon wheel."""
    
    @patch('sys.stdout')
    def test_complete_animation_cycle(self, mock_stdout):
        """Complete animation cycle should work end-to-end."""
        wheel = WagonWheel(width=60, speed='fast', enabled=True)
        wheel.roll(duration_ms=100)
        # Should have called write multiple times
        assert mock_stdout.write.call_count > 0
    
    def test_multiple_wheels_independent(self):
        """Multiple wheel instances should be independent."""
        wheel1 = WagonWheel(width=60, speed='fast', enabled=False)
        wheel2 = WagonWheel(width=80, speed='slow', enabled=False)
        assert wheel1.width != wheel2.width
        assert wheel1.speed != wheel2.speed
    
    @patch('sys.stdout')
    def test_sequential_animations(self, mock_stdout):
        """Should handle sequential animations."""
        wheel = WagonWheel(width=60, enabled=True)
        wheel.roll(duration_ms=50)
        wheel.pulse()
        # Both should complete without error
        assert mock_stdout.write.called


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
