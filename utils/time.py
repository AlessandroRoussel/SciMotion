"""
Utilitary functions to manipulate durations.

The Time class provides utilitary functions
to manipulate times, frames, durations...
"""

import numpy as np


class Time:
    """Utilitary functions to manipulate durations."""

    @staticmethod
    def format_duration(frames: int, fps: int) -> str:
        """Return a 'h:mm:ss.ff' formatted string representing a duration."""
        _frames = int(frames % fps)
        _seconds = int(np.floor(frames/fps)) % 60
        _minutes = int(np.floor(frames/fps/60)) % 60
        _hours = int(np.floor(frames/fps/3600))

        _str_frames = ("0" if _frames < 10 else "") + str(_frames)
        _str_seconds = ("0" if _seconds < 10 else "") + str(_seconds)
        _str_minutes = ("0" if _minutes < 10 else "") + str(_minutes)
        _str_hours = str(_hours)

        return f"{_str_hours}:{_str_minutes}:{_str_seconds}.{_str_frames}"
