"""
Utilitary functions to manipulate times.

The Time class provides utilitary functions
to manipulate times, frames, durations...
"""

import numpy as np


class Time:
    """Utilitary functions to manipulate times."""

    @staticmethod
    def format_time(frame: int, fps: float, short: bool = False) -> str:
        """Return a 'h:mm:ss.f' formatted string representing a time."""
        _frames = int(frame % fps)
        _seconds = int(np.floor(frame/fps)) % 60
        _minutes = int(np.floor(frame/fps/60)) % 60
        _hours = int(np.floor(frame/fps/3600))

        _str_sec = ("0" if _seconds < 10 and not short else "") + str(_seconds)
        _str_min = ("0" if _minutes < 10 and not short else "") + str(_minutes)

        _str_fra = str(_frames)
        while len(_str_fra) < len(str(int(np.ceil(fps-1)))):
            _str_fra = "0" + _str_fra
        _str_fra = ("." + _str_fra) if _frames != 0 or not short else ""

        if not short or _hours != 0:
            return f"{_hours}:{_str_min}:{_str_sec}{_str_fra}"
        elif _minutes != 0:
            return f"{_str_min}:{_str_sec}{_str_fra}"
        else:
            return f"{_str_sec}{_str_fra}"