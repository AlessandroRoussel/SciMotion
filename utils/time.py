"""
Utilitary functions to manipulate times.

The Time class provides utilitary functions
to manipulate times, frames, durations...
"""

import numpy as np


class Time:
    """Utilitary functions to manipulate times."""

    @staticmethod
    def format_time(frames: int, fps: int) -> str:
        """Return a 'h:mm:ss.f' formatted string representing a time."""
        _frames = int(frames % fps)
        _seconds = int(np.floor(frames/fps)) % 60
        _minutes = int(np.floor(frames/fps/60)) % 60
        _hours = int(np.floor(frames/fps/3600))

        _str_seconds = ("0" if _seconds < 10 else "") + str(_seconds)
        _str_minutes = ("0" if _minutes < 10 else "") + str(_minutes)

        return f"{_hours}:{_str_minutes}:{_str_seconds}.{_frames}"
