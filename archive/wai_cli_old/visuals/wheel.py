"""
Wagon Wheel Animation

The signature visual element of the Wheelwright CLI.
Rolling wagon wheel appearing on major operations (init, learn, teach).
"""

import time
import os
import sys
from typing import Optional


class WagonWheel:
    """ASCII wagon wheel rolling animation.
    
    A 12-frame rotating wheel that rolls left to right across the terminal.
    Configurable speed and width. Gracefully handles non-TTY environments.
    """

    # 12 frames of wagon wheel rotation
    FRAMES = [
        "◎───────────────────────────────────────────────────────",
        "─◐──────────────────────────────────────────────────────",
        "──◑─────────────────────────────────────────────────────",
        "───◒────────────────────────────────────────────────────",
        "────◓───────────────────────────────────────────────────",
        "─────◔──────────────────────────────────────────────────",
        "──────◕─────────────────────────────────────────────────",
        "───────◖────────────────────────────────────────────────",
        "────────◉───────────────────────────────────────────────",
        "───────◎────────────────────────────────────────────────",
        "──────◐─────────────────────────────────────────────────",
        "─────◑──────────────────────────────────────────────────",
    ]

    def __init__(
        self,
        width: int = 60,
        frames: int = 12,
        speed: str = "medium",
        enabled: bool = True
    ):
        """Initialize wagon wheel.
        
        Args:
            width: Terminal width for animation (chars)
            frames: Number of animation frames (default: 12)
            speed: Animation speed ('fast', 'medium', 'slow')
            enabled: Whether to animate (auto-disable in non-TTY)
        """
        self.width = width
        self.frames = frames
        self.speed = speed
        self._set_frame_delay()
        
        # Auto-detect non-TTY environment
        self.enabled = enabled and self._is_tty()
    
    def _is_tty(self) -> bool:
        """Check if stdout is a TTY (not piped/CI)."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def _set_frame_delay(self):
        """Set frame delay based on speed."""
        speed_map = {
            'fast': 0.05,
            'medium': 0.08,
            'slow': 0.12
        }
        self.frame_delay = speed_map.get(self.speed, 0.08)
    
    def roll(self, duration_ms: int = 3000) -> None:
        """Animate wagon rolling left to right.
        
        Args:
            duration_ms: Animation duration in milliseconds
        """
        if not self.enabled:
            return
        
        num_frames = int(duration_ms / (self.frame_delay * 1000))
        frame_cycle = len(self.FRAMES)
        
        try:
            for i in range(num_frames):
                frame_idx = i % frame_cycle
                frame = self.FRAMES[frame_idx]
                
                # Pad to width if needed
                if len(frame) < self.width:
                    frame = frame + '─' * (self.width - len(frame))
                else:
                    frame = frame[:self.width]
                
                # Print and overwrite
                sys.stdout.write(f"\r{frame}")
                sys.stdout.flush()
                time.sleep(self.frame_delay)
            
            # Clear line
            sys.stdout.write(f"\r{' ' * self.width}\r")
            sys.stdout.flush()
        
        except KeyboardInterrupt:
            # Gracefully handle Ctrl+C
            sys.stdout.write(f"\r{' ' * self.width}\r")
            sys.stdout.flush()
    
    def pulse(self) -> None:
        """Brief pulse animation (inline use)."""
        if not self.enabled:
            return
        
        # Quick 2-frame pulse
        for frame in [self.FRAMES[0], self.FRAMES[6]]:
            sys.stdout.write(f"\r{frame}")
            sys.stdout.flush()
            time.sleep(0.1)
        
        sys.stdout.write(f"\r{' ' * self.width}\r")
        sys.stdout.flush()
    
    def get_frame(self, frame_num: int) -> str:
        """Get a specific frame (for testing).
        
        Args:
            frame_num: Frame index (0-11)
        
        Returns:
            Frame string padded to width
        """
        frame = self.FRAMES[frame_num % len(self.FRAMES)]
        if len(frame) < self.width:
            frame = frame + '─' * (self.width - len(frame))
        return frame[:self.width]
    
    def render_all_frames(self) -> list:
        """Get all frames (for testing/demo)."""
        return [self.get_frame(i) for i in range(len(self.FRAMES))]


# Global singleton instance
_wheel_instance: Optional[WagonWheel] = None


def get_wagon_wheel(
    width: int = 60,
    speed: str = "medium",
    enabled: bool = True
) -> WagonWheel:
    """Get or create wagon wheel instance.
    
    Args:
        width: Terminal width
        speed: Animation speed
        enabled: Whether to animate
    
    Returns:
        WagonWheel instance
    """
    global _wheel_instance
    if _wheel_instance is None:
        _wheel_instance = WagonWheel(width=width, speed=speed, enabled=enabled)
    return _wheel_instance


def reset_wheel():
    """Reset the global wagon wheel instance (for testing)."""
    global _wheel_instance
    _wheel_instance = None
